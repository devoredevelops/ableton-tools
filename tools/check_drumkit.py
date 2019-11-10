import logging
import os.path
logging.basicConfig(level=logging.DEBUG)

from argparse import ArgumentParser

from pyableton import AbletonCollection


def get_args():
    p = ArgumentParser(description='Check what samples in a drumkit are used in all your ableton projects')
    p.add_argument('path', help='Path to sample file or drumkit folder')
    p.add_argument('--collection', help='(e.g. ~/Music/Ableton)', default='~/Music/Ableton')
    return p.parse_args()


def main():
    args = get_args()

    try:
        collection = AbletonCollection(args.collection)
    except IOError:
        print(f'{args.collection} not found')
        return

    if os.path.isdir(args.path):
        usage = collection.check_dir_used(args.path)

        for file, usa in usage.items():
            print(file)
            for proj, sets in usa.items():
                print('\t', proj)
                for set in sets:
                    print('\t\t', set)
    else:
        usa = collection.check_file_used(args.path)
        for proj, sets in usa.items():
            print(proj)
            for set in sets:
                print('\t', set)


if __name__ == '__main__':
    main()
