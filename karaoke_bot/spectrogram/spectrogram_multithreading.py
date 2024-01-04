import librosa
import os
import time
import threading
from queue import Queue


def get_audio_sample(audio, sr, start, duration):
    return audio[start * sr:(start + duration) * sr]


def get_spectrogram_pair(
        audio,
        sr,
        start: int,
        duration: int,
        overlap: int,
        volume: int = 1,
        frame_size: int = 2048,
        hop_size: int = 512
):

    sample1 = get_audio_sample(audio, sr, start=start, duration=duration) * volume
    sample2 = get_audio_sample(audio, sr, start=start + duration - overlap, duration=duration) * volume

    spec1 = librosa.stft(sample1, n_fft=frame_size, hop_length=hop_size)
    spec2 = librosa.stft(sample2, n_fft=frame_size, hop_length=hop_size)

    return spec1, spec2


def get_wav_spectrograms(file_path: str, pairs: int):
    y, sr = librosa.load(file_path, sr=44100, mono=True)
    wav_specrtograms = []
    for i in range(pairs):
        start = 30 + i * 5
        sp1, sp2 = get_spectrogram_pair(audio=y, sr=sr, start=start, duration=20, overlap=5)
        wav_specrtograms.append(sp1)
        wav_specrtograms.append(sp2)

    return wav_specrtograms


def process_files(
        filenames: list,
        folder_path: str,
        lock,
        result_queue: Queue,
        processed_files_counter: list[int],
        max_files: int):

    while True:
        with lock:  # блокируем мьютекс
            if not filenames or processed_files_counter[0] >= max_files:
                break
            filename = filenames.pop(0)
            processed_files_counter[0] += 1

        wav_spectrograms = get_wav_spectrograms(file_path=os.path.join(folder_path, filename), pairs=8)
        result_queue.put(wav_spectrograms, block=True)


if __name__ == '__main__':
    folder_path = r'D:\PROGRAMMS\PYTHON_PROJECTS\youtube_parse\tracks_wav'
    filenames = os.listdir(folder_path)

    workers = 4  # Желаемое количество потоков
    processed_files_counter = [0]  # Счетчик обработанных файлов
    max_files_to_process = 10  # Максимальное количество файлов для обработки

    start_time = time.time()
    result_queue = Queue()
    lock = threading.Lock()  # Создаем мьютекс

    threads = []
    for _ in range(workers):
        thread = threading.Thread(
            target=process_files,
            args=(
                filenames,
                folder_path,
                lock,
                result_queue,
                processed_files_counter,
                max_files_to_process
            )
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    execution_time = time.time() - start_time
    print(f"Processing completed in {execution_time} seconds")
