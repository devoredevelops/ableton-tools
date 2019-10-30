import xml.etree.ElementTree as ET
import pickle
import os
import os.path
import logging

logging.basicConfig(level=logging.DEBUG)

import gzip
from argparse import ArgumentParser

'''
./tool samplefile.wave ableton.als

decompress it in memory
parse the xml
'''

class AbletonCollection:
    '''
    A collection of projects.
    '''

    def __init__(self, dirname):
        self.dirname = os.path.expanduser(dirname)
        self.projects = {}  # Map dirpaths to projects
        self._find_projects()

    def check_file_used(self, filename):
        used = {}
        for projpath, proj in self.projects.items():
            sets = proj.check_file_used(filename) 
            if sets:
                used[projpath] = sets
        return used

    def check_dir_used(self, dirname):
        used = {}
        for dirpath, dirnames, filenames in os.walk(dirname):
            for fname in filenames:
                full = os.path.join(dirpath, fname)
                results = self.check_file_used(full)
                if results:
                    used[fname] = results
        return used

    def _get_existing_project(self, dirpath):
        """
        Check if dirpath is within an existing project, or not.
        Progressively cut off the end of the path and check if its an existing
        project.
        """
        existing = ''

        while dirpath and dirpath != '/':
            inside_existing_project = dirpath in self.projects
            if inside_existing_project:
                existing = dirpath
                break
            else:
                dirpath = os.path.dirname(dirpath)

        return existing

    def _find_projects(self):
        """
        Search dir for all projects and sets.
        """
        for dirpath, dirnames, filenames in os.walk(self.dirname):
            # print(dirpath, dirnames, filenames)

            # Backup dirs have extra als sets that we might not care about.
            # Might slow things down a lot. Not sure if we want them yet.
            # Checking `in` and not `endswith` bc if you create dirs inside
            # an existing project, that dir structure will be recreated in
            # the Backup dir, and those dirs won't end with `Backup`
            if 'Backup' in dirpath:
                continue

            set_names = [fname for fname in filenames if fname.endswith('.als')]
            if not set_names:
                continue

            # print(set_names)

            # if set names, and its def a new project, create new

            # if set names, but not a new project, just add these sets
            # to that project. requires quick way to look up a set by
            # its name - dict

            set_paths = [os.path.join(dirpath, sname) for sname in set_names]
            # sets = [AbletonSet.fromfile(spath, lazy=True) for spath in set_paths]
            sets = [AbletonSet.fromfile(spath, lazy=False) for spath in set_paths]

            existing_dirpath = self._get_existing_project(dirpath)
            if existing_dirpath:
                proj = self.projects[existing_dirpath]
                proj.sets += sets
            else:
                pname = os.path.basename(dirpath)
                proj = AbletonProject(pname, dirpath)
                proj.sets = sets
                self.projects[dirpath] = proj

                logging.debug(f'Added new proj: {pname}')
                # print(proj, proj.sets)

class AbletonProject:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.sets = []

    def check_file_used(self, filename):
        sets = []
        for set in self.sets:
            if set.check_file_used(filename):
                sets.append(set.name)
        return sets

    def __repr__(self):
        return f'<{self.path} AbletonProject>'

class AbletonSet:
    @classmethod
    def fromfile(cls, filename, **kwargs):
        with gzip.open(os.path.expanduser(filename)) as f:
            return cls(f.read(), name=filename, **kwargs)

    def __repr__(self):
        return f'<{self.name} AbletonSet>'

    def __init__(self, xml, name='', lazy=False):
        self.name = name
        self.raw_xml = xml
        self.parsed_xml = None

        # Files used by this Ableton set. Equivalent to the Ableton
        # 'View Files' button in File Manager
        self.files = set()

        if not lazy:
            self.parse()

    def parse(self):
        # self.parsed_xml = ET.fromstring(self.raw_xml)

        # self.files = self._get_files()
        self.files = self._get_files_fast()

    def _get_files(self):
        files = set()
        for elem in self.parsed_xml.iter():
            if elem.tag == 'SampleRef':
                file_ref_elem = elem.find('FileRef')
                name_elem = file_ref_elem.find('Name')
                sample_filename = name_elem.attrib['Value']
                files.add(sample_filename)
        return files

    def _get_files_fast(self):
        START_TAG = b'<SampleRef>'
        END_TAG = b'</SampleRef>'

        files = set()
        pos = 0
        while True:
            start = self.raw_xml.find(START_TAG, pos)
            if start == -1:
                break
            end = self.raw_xml.find(END_TAG, start) + len(END_TAG)

            pos = end

            sample_ref_str = self.raw_xml[start:end]
            sample_ref_elem = ET.fromstring(sample_ref_str)
            file_ref_elem = sample_ref_elem.find('FileRef')
            name_elem = file_ref_elem.find('Name')
            sample_filename = name_elem.attrib['Value']
            files.add(sample_filename)


            # import ipdb; ipdb.set_trace()

        return files

    def check_file_used(self, filename):
        # print(os.path.basename(filename))
        # print(self.files)
        return os.path.basename(filename) in self.files

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


