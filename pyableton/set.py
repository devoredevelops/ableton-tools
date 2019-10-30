import gzip
import os.path
import logging

import xml.etree.ElementTree as ET

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

        return files

    def check_file_used(self, filename):
        return os.path.basename(filename) in self.files
