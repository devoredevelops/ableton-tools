import pickle

import logging
logging.basicConfig(level=logging.DEBUG)

from argparse import ArgumentParser

from pyableton import AbletonCollection, AbletonProject, AbletonSet

'''
./tool samplefile.wave ableton.als

decompress it in memory
parse the xml
'''




def get_args():
    p = ArgumentParser()
    p.add_argument('sample')
    p.add_argument('als')
    return p.parse_args()


def main():
    args = get_args()

    try:
        aset = AbletonSet.fromfile(args.als)
    except IOError:
        print(f'{args.als} not found')
        return

    is_used = aset.check_file_used(args.sample)
    print(is_used)


def test():
    s = AbletonSet.fromfile('~/Music/Ableton/dan shay Project/dan shay.als')
    print(s.files)
    print(len(s.files))
    assert len(s.files) == 26

def test_coll():
    coll = AbletonCollection('~/Music/Ableton')
    print(coll.projects.keys())
    # import IPython; IPython.embed()

def test_check_coll():
    coll = AbletonCollection('~/Music/Ableton')
    # print(coll.check_file_used('Perfect White Noise Transition.wav'))
    # print(coll.check_file_used("Kick Nebula Hard.aif"))
    print(coll.check_file_used("natural crash.wav"))

def test_check_pack():
    coll = AbletonCollection('~/Music/Ableton')
    # print(coll.check_file_used('Perfect White Noise Transition.wav'))
    # print(coll.check_file_used("Kick Nebula Hard.aif"))
    usage = coll.check_dir_used("/Users/mark/music/recording/samples/_drumkits/ginseng drum kit VOL 3")
    for file, usa in usage.items():
        print(file)
        for proj, sets in usa.items():
            print('\t', proj)
            for set in sets:
                print('\t\t', set)


# main()
# test()
# test_coll()
# test_check_coll()
test_check_pack()


