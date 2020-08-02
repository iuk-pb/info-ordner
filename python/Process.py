import os.path


class Process:
    def __init__(self, info_file):
        self.infoFile = info_file
        self.outputFiles = []
        self.folderCache = None
        self.folderWork = None

    def add_output_file(self, file):
        self.outputFiles.append(file)

    def need_create_cache(self):
        for file in self.outputFiles:
            if not os.path.exists(file):
                return True

    def cache_files(self):
        return self.outputFiles
