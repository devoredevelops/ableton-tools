import os
import os.path
import logging

from .set import AbletonSet
from .project import AbletonProject


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

            set_paths = [os.path.join(dirpath, sname) for sname in set_names]
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
