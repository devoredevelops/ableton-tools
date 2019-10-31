from pyableton import AbletonSet, AbletonCollection

class TestBasics:
    def test_files(self):
        s = AbletonSet.fromfile('tests/data/testproject Project/testproject.als')
        assert len(s.files) == 4
        assert s.files == {"chirp Cosmic's Fx 25.wav", '[Hi Hat] Bompton.wav', 'natural crash.wav', "Cosmic's 808 2 C.wav"}
        assert not s.check_file_used('blah')
        assert s.check_file_used('[Hi Hat] Bompton.wav')

    def test_files2(self):
        s = AbletonSet.fromfile('tests/data/testproj2 Project/testproj2.als')
        assert len(s.files) == 2
        assert s.files == {"Cosmic's 808 2 C.wav", 'EK-Kick-Blessings.wav'}

    def test_coll(self):
        c = AbletonCollection('tests/data')
        assert len(c.projects) == 2
        assert len(c.projects['tests/data/testproject Project'].sets) == 2
        assert len(c.projects['tests/data/testproj2 Project'].sets) == 1

class TestCheck:
    def test_check_file_used(self):
        c = AbletonCollection('tests/data')
        assert c.check_file_used('natural crash.wav')
        assert not c.check_file_used('natural X crash.wav')

    def test_check_dir_used(self):
        c = AbletonCollection('tests/data')
        results = c.check_dir_used('tests/data/drumkit')
        correct_results = {'natural crash.wav': {'tests/data/testproject Project': ['tests/data/testproject Project/testproject.als', 'tests/data/testproject Project/subdir/subtestproject.als']}, '[Hi Hat] Bompton.wav': {'tests/data/testproject Project': ['tests/data/testproject Project/testproject.als', 'tests/data/testproject Project/subdir/subtestproject.als']}, "Cosmic's 808 2 C.wav": {'tests/data/testproject Project': ['tests/data/testproject Project/testproject.als', 'tests/data/testproject Project/subdir/subtestproject.als'], 'tests/data/testproj2 Project': ['tests/data/testproj2 Project/testproj2.als']}, 'EK-Kick-Blessings.wav': {'tests/data/testproj2 Project': ['tests/data/testproj2 Project/testproj2.als']}}
        assert results == correct_results


