import Process
import os.path
import glob
import Utils


def create_instance(info_file):
    return ProcessSla(info_file)


class ProcessSla(Process.Process):
    def __init__(self, info_file):
        Process.Process.__init__(self, info_file)

    def create_cache(self, folder_cache, folder_work, contacts, variables, input_folders):
        self.folderCache = folder_cache
        self.folderWork = folder_work

        output_file = self.folderCache + "/" + self.infoFile.baseFile + ".pdf"
        self.add_output_file(output_file)

        if not self.need_create_cache():
            # No update of the cache is required, return
            return

        tmp_sla = self.folderWork + "/" + self.infoFile.baseFile + ".sla"
        raw_sla = self.infoFile.file.replace(".yaml", ".sla")
        if 'sla' in self.infoFile.raw_yaml:
            raw_sla = os.path.dirname(self.infoFile.file) + "/" + self.infoFile.raw_yaml['sla']
            if not os.path.exists(raw_sla):
                # Not direct path, check each input folder
                for inputFolder in input_folders:
                    raw_sla = inputFolder + "/" + self.infoFile.raw_yaml['sla']
                    if os.path.exists(raw_sla):
                        break

        raw_without_extension = raw_sla.replace(".sla", ".*")
        additional_files = glob.glob(raw_without_extension)
        for file in additional_files:
            Utils.syscall("cp '" + file + "' '" + self.folderWork + "/'")

        # Process raw files
        data = ''
        with open(raw_sla, 'r') as file:
            data = file.read()

        data = data.replace("%DOCID%", self.infoFile.docId)
        data = data.replace("%DOCTITLE%", self.infoFile.docTitle)
        data = data.replace("%DATUM%", self.infoFile.datum)
        data = data.replace("%VERSION%", self.infoFile.version)

        for key in self.infoFile.variables:
            data = data.replace("%" + key + "%", self.infoFile.variables[key])

        for key in variables:
            data = data.replace("%" + key + "%", variables[key])

        data = contacts.replace_data(data, "%", "%")

        with open(tmp_sla, 'w') as file:
            file.write(data)

        scribus_python_file = os.path.dirname(os.path.abspath(__file__)) + "/ScribusExport.py"

        Utils.syscall(
            'INFOFILE_SLA_IN="' + tmp_sla + '" INFOFILE_SLA_OUT="' + output_file + '" scribus-ng -g -py ' +
            scribus_python_file)
