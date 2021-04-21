class AbletonProject:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.sets = []

    def check_file_used(self, filename):
        return [set.name for set in self.sets if set.check_file_used(filename)]

    def __repr__(self):
        return f'<{self.path} AbletonProject>'
