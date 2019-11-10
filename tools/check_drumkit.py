import logging
logging.basicConfig(level=logging.DEBUG)

from argparse import ArgumentParser

from pyableton import AbletonCollection


def get_args():
    p = ArgumentParser(description='Check what samples in a drumkit are used in all your ableton projects')
    p.add_argument('--drumkit', help='Path to drumkit', required=True)
    p.add_argument('--collection', help='(e.g. ~/Music/Ableton)', default='~/Music/Ableton')
    return p.parse_args()


def main():
    args = get_args()

    try:
        collection = AbletonCollection(args.collection)
    except IOError:
        print(f'{args.collection} not found')
        return

    usage = collection.check_dir_used(args.drumkit)

    for file, usa in usage.items():
        print(file)
        for proj, sets in usa.items():
            print('\t', proj)
            for set in sets:
                print('\t\t', set)

if __name__ == '__main__':
    main()
