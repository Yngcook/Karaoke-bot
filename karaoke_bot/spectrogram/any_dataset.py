import threading
from sklearn.utils import shuffle
import numpy as np
import os
import random
import librosa
from audio_processing import get_spectrograms


class ThreadSafeIter:
    """
    Takes an iterator/generator and makes it thread-safe by
    serializing call to the `next` method of given iterator/generator.
    """

    def __init__(self, iterator):
        self.it = iterator
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.it)


def get_objects_i(objects_count):
    """
    Cyclic generator of paths indices
    """
    current_objects_id = 0
    while True:
        yield current_objects_id
        current_objects_id = (current_objects_id + 1) % objects_count


class RandomIndexGenerator:  # Выдает случайные индексы, при достижении последнего индекса, начинает перебор заново
    def __init__(self, max_index):
        self.max_index = max_index
        self.indices = list(range(max_index))
        self.current_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_index == 0:
            random.shuffle(self.indices)  # Перемешиваем индексы перед каждым новым циклом

        if self.current_index >= self.max_index:
            self.current_index = 0  # Начинаем заново, если достигли конца списка индексов

        result = self.indices[self.current_index]
        self.current_index += 1
        return result


def get_random_index_except(max_index: int, current_index: int):
    random_index = random.randint(0, max_index - 1)

    # Повторяем генерацию, пока не получим индекс, отличный от current_index
    while random_index == current_index:
        random_index = random.randint(0, max_index - 1)

    return random_index


class SpectrogramGenerator:

    def __init__(
            self,
            folder_path: str,
            batch_size: int,
            sr: float,
            start: float,
            duration: float,
            overlap: float
    ):
        self.folder_path = folder_path
        self.data = os.listdir(self.folder_path)

        self.batch_size = batch_size
        self.batch_data = []

        self.objects_id_generator = ThreadSafeIter(RandomIndexGenerator(len(self.data)))

        # Аттрибуты для получения спектрограмм
        self.sr = sr
        self.start = start
        self.duration = duration
        self.overlap = overlap

        self.lock = threading.Lock()
        self.batch_data_lock = threading.Lock()

    def __len__(self):
        return len(self.data)

    def _load_audio(self, filename):
        return librosa.load(path=os.path.join(self.folder_path, filename), sr=self.sr)

    def _get_spectrograms(self, audio, n_samples):
        return get_spectrograms(audio, self.sr, n_samples, self.start, self.duration, self.overlap)

    def __iter__(self):
        return self

    def _generate_batch_data(self, spectrs1, spectrs2, dissim_spectrs):
        with self.batch_data_lock:

            if len(self.batch_data) < self.batch_size:
                for sp1, sp2, sp in zip(spectrs1, spectrs2, dissim_spectrs):
                    self.batch_data.append((sp1, sp2, True))
                    self.batch_data.append((sp1, sp, False))

            if len(self.batch_data) >= self.batch_size:
                print(len(self.batch_data))
                batch_x1 = [a[0] for a in self.batch_data]
                batch_x2 = [a[1] for a in self.batch_data]
                batch_y = [a[2] for a in self.batch_data]

                self.batch_data = []
                return batch_x1, batch_x2, batch_y

    def __next__(self):
        with self.lock:
            obj_id = next(self.objects_id_generator)
            filename = self.data[obj_id]

        y1, _ = self._load_audio(filename)
        spectrs = self._get_spectrograms(audio=y1, n_samples=self.batch_size)
        sim_sp1 = spectrs[::2]
        sim_sp2 = spectrs[1::2]

        another_idx = get_random_index_except(max_index=len(self.data), current_index=obj_id)
        with self.lock:
            another_filename = self.data[another_idx]

        y2, _ = self._load_audio(another_filename)
        dissim_sp = self._get_spectrograms(audio=y2, n_samples=self.batch_size // 2)

        return self._generate_batch_data(sim_sp1, sim_sp2, dissim_sp)


if __name__ == "__main__":
    SR = 44100
    # WORKERS = 4  # Желаемое количество потоков
    BATCH_SIZE = 16
    START_TIME = 20
    DURATION = 10
    OVERLAP = 7

    folder_path = r'D:\PROGRAMMS\PYTHON_PROJECTS\youtube_parse\tracks_wav'
    filenames = os.listdir(folder_path)

    sp_gen = SpectrogramGenerator(
        folder_path=folder_path,
        batch_size=BATCH_SIZE,
        sr=SR,
        start=START_TIME,
        duration=DURATION,
        overlap=OVERLAP
    )

    count = 0
    for batch_x1, batch_x2, batch_y in sp_gen:
        # print(len(batch_x1), len(batch_x2), batch_y)
        count += 1
        if count >= 10:
            break
