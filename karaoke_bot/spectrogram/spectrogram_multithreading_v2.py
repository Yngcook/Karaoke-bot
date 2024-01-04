import librosa
import os
import time
import threading
from queue import Queue
from audio_processing import get_spectrograms
import matplotlib.pyplot as plt
import numpy as np


def process_files(
        folder_path: str,
        filenames: list[str],
        lock: threading.Lock,
        result_queue: Queue,
        processed_files_counter: list[int],
        max_files: int
):

    while True:
        with lock:  # блокируем мьютекс
            if not filenames or processed_files_counter[0] >= max_files:
                break
            filename = filenames.pop(0)
            processed_files_counter[0] += 1

        y, sr = librosa.load(path=os.path.join(folder_path, filename), sr=SR)
        wav_spectrograms = get_spectrograms(
            audio=y,
            sr=sr,
            n_samples=NUM_SAMPLES,
            start=START_TIME,
            duration=DURATION,
            overlap=OVERLAP
        )
        result_queue.put(wav_spectrograms, block=True)


if __name__ == '__main__':
    SR = 44100
    WORKERS = 4  # Желаемое количество потоков
    MAX_FILES_TO_PROCESS = 10
    NUM_SAMPLES = 8
    START_TIME = 20
    DURATION = 10
    OVERLAP = 5

    folder_path = r'D:\PROGRAMMS\PYTHON_PROJECTS\youtube_parse\tracks_wav'
    filenames = os.listdir(folder_path)

    processed_files_counter = [0]  # Счетчик обработанных файлов

    start_time = time.time()
    result_queue = Queue()
    lock = threading.Lock()  # Создаем мьютекс

    threads = []
    for _ in range(WORKERS):
        thread = threading.Thread(
            target=process_files,
            args=(
                folder_path,
                filenames,
                lock,
                result_queue,
                processed_files_counter,
                MAX_FILES_TO_PROCESS
            )
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    execution_time = time.time() - start_time
    print(f"Processing completed in {execution_time} seconds")

    # y, sr = librosa.load(path=os.path.join(folder_path, filenames[0]), sr=SR)
    # wav_spectrograms = get_spectrograms(audio=y, sr=sr, n_samples=8, start=20, duration=20, overlap=15)
    # for index, spectr in enumerate(wav_spectrograms, start=1):
    #     plt.subplot(8, 1, index)
    #     librosa.display.specshow(librosa.amplitude_to_db(np.abs(spectr), ref=np.max), sr=sr, y_axis='log', x_axis='time')
    #     # plt.colorbar(format='%+2.0f dB')
    # plt.show()

