import Process


def create_instance(info_file):
    return ProcessLink(info_file)


class ProcessLink(Process.Process):
    def __init__(self, info_file):
        Process.Process.__init__(self, info_file)

    def create_cache(self, folder_cache, folder_work, contacts, variables, input_folders):
        # Nothing to be done
        return
