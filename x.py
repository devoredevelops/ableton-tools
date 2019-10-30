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

    def __repr__(self):
        return f'<{self.path} AbletonProject>'

class AbletonSet:
    SUPPORTED_VERSION = 5

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
        self.major_version = None

        # Files used by this Ableton set. Equivalent to the Ableton
        # 'View Files' button in File Manager
        self.files = set()

        if not lazy:
            self.parse()

    def parse(self):
        self.parsed_xml = ET.fromstring(self.raw_xml)
        self.major_version = self._get_major_version()

        # TODO: maybe rm this
        self._check_version()

        self.files = self._get_files()

    def _check_version(self):
        pass
        # if self.major_version != self.SUPPORTED_VERSION:
        #     raise Exception('Unsupported set version')

    def _get_major_version(self):
        return int(self.parsed_xml.attrib['MajorVersion'])

    def _get_files(self):
        files = set()
        for elem in self.parsed_xml.iter():
            if elem.tag == 'SampleRef':
                file_ref_elem = elem.find('FileRef')
                name_elem = file_ref_elem.find('Name')
                sample_filename = name_elem.attrib['Value']
                files.add(sample_filename)
        return files

    def check_file_used(self, filename):
        return os.path.basename(filename) in self.files

def get_args():
    p = ArgumentParser()
    p.add_argument('sample')
    p.add_argument('als')
    return p.parse_args()


def main():
    args = get_args()
    # sample can be fullpath or just base

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
    assert s.major_version == 5

def test_coll():
    coll = AbletonCollection('~/Music/Ableton')
    print(coll.projects)
    # import IPython; IPython.embed()

# main()
# test()
test_coll()


