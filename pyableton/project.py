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
