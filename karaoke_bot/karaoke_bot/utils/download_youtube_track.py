import argparse
from music2vec.extraction import Extractor
from yt_dlp import YoutubeDL
import os


def download_video_youtube(url: str):
    outtmpl = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracks_wav', '%(title)s.%(ext)s')
    cachedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracks_cache')
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': outtmpl,
        'cachedir': cachedir,
        'noplaylist': True,
        'extractaudio': True,
        'no_cache_dir': True,
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        # error_code = ydl.download(url)
        info = ydl.extract_info(url, download=True)

    # filename = os.path.basename(info['filepath'])

    filename = info.get('title')
    filename += '.wav'
    return filename


def wav2vec(file_wav):
    extractor = Extractor()
    genres, features = extractor(file_wav)
    print(*genres)
    print(*features)


def create_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        title='subcommands',
        description="All subcommands",
        help="When typing a subcommand, the corresponding function of the same name will be called.",
        dest='subparser_name')

    parser_download = subparsers.add_parser('dwld')
    parser_download.add_argument('link', type=str)

    parser_music2vec = subparsers.add_parser('m2v')
    parser_music2vec.add_argument('filepath', type=str)

    parser_convert = subparsers.add_parser('convert')
    parser_convert.add_argument('link')
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.subparser_name == 'dwld':
        # print(json.dumps(download_video_youtube(url=args.link), indent=4))
        print(download_video_youtube(url=args.link))

    if args.subparser_name == 'm2v':
        wav2vec(file_wav=args.filepath)
