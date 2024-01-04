import librosa
import matplotlib.pyplot as plt
import numpy as np
import os
import time


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


def plot(spectr):
    plt.subplot(2, 2, 1)
    librosa.display.specshow(
        librosa.amplitude_to_db(np.abs(spectr), ref=np.max),
        sr=sample_rate,
        y_axis='log',
        x_axis='time'
    )
    plt.colorbar(format='%+2.0f dB')
    plt.title('sample1 V1')

    plt.subplot(2, 2, 2)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec1v2), ref=np.max), sr=sample_rate, y_axis='log',
                             x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('sample2 V1')

    plt.subplot(2, 2, 3)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec2v1), ref=np.max), sr=sample_rate, y_axis='log',
                             x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('sample1 V2')

    plt.subplot(2, 2, 4)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec2v2), ref=np.max), sr=sample_rate, y_axis='log',
                             x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('sample2 V2')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    folder_path = r'D:\PROGRAMMS\PYTHON_PROJECTS\youtube_parse\tracks_wav'
    filenames = os.listdir(folder_path)
    number_sample_pairs = 8

    start_time = time.time()
    for filename in filenames[:10]:  # оценим производительность на первых 10 файлах

        y, sr = librosa.load(os.path.join(folder_path, filename), sr=44100, mono=True)
        for i in range(number_sample_pairs):
            start = 30 + i * 5
            sp1, sp2 = get_spectrogram_pair(audio=y, sr=sr, start=start, duration=20, overlap=5)

            # plt.subplot(number_sample_pairs * 2, 2, (i + 1)*2 - 1)
            # librosa.display.specshow(librosa.amplitude_to_db(np.abs(sp1), ref=np.max), sr=sr, y_axis='log', x_axis='time')
            # plt.colorbar(format='%+2.0f dB')
            # plt.title(f'sample{(i + 1)*2 - 1}')
            #
            # plt.subplot(number_sample_pairs * 2, 2, (i + 1)*2)
            # librosa.display.specshow(librosa.amplitude_to_db(np.abs(sp2), ref=np.max), sr=sr, y_axis='log', x_axis='time')
            # plt.colorbar(format='%+2.0f dB')
            # plt.title(f'sample{(i + 1)*2}')
        # plt.show()
        # break
    execution_time = time.time() - start_time
    print(f"Выполнено за {execution_time} секунд")

