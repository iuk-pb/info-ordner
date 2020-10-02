import Process
import os.path
import glob
import shutil


def create_instance(info_file):
    return ProcessCopy(info_file)


class ProcessCopy(Process.Process):
    def __init__(self, info_file):
        Process.Process.__init__(self, info_file)

    def create_cache(self, folder_cache, folder_work, contacts, variables, input_folders):
        self.folderCache = folder_cache
        self.folderWork = folder_work

        file = self.infoFile.file.replace(".yaml", ".*")
        files = glob.glob(file)

        for f in files:
            if not f.endswith(".yaml"):
                self.add_output_file(self.folderCache + "/" + os.path.basename(f))

        if not self.need_create_cache():
            # No update of the cache is required, return
            return

        for f in files:
            if not f.endswith(".yaml"):
                shutil.copy(f, self.folderCache)
