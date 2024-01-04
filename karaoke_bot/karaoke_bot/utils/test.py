from music2vec.music2vec.extraction import Extractor
from music2vec.music2vec.dataset import GENRES
from scipy.spatial import distance


def wav2vec(filepath):
    extractor = Extractor()
    genres, features = extractor(filepath)
    return genres, features


if __name__ == '__main__':
    genre_values, _ = wav2vec('Григорий_Лепс_x_Ирина_Аллегрова-Я_тебе_не верю.mp3')
    genre_values_minus, _ = wav2vec('Григорий_Лепс_x_Ирина_Аллегрова-Я_тебе_не_верю_минус.mp3')
    genre_values = [float(v) for v in genre_values]
    genre_values_minus = [float(v) for v in genre_values_minus]

    print(f'Косинусное расстояние: {round(distance.cosine(genre_values, genre_values_minus), 4)}')

    for v1, v2, genre in zip(genre_values, genre_values_minus, GENRES):
        print(f'Жанр: {genre}', end=' ')
        print(f'Оригинал: {round(v1, 4)}, Инструментал {round(v2, 4)}, модуль разности: {round(abs(v1 - v2), 4)}')
