import yaml
import os.path
import shutil
import logging
import Utils

logger = logging.getLogger("InfoFile")


class Set:
    def __init__(self, name, printed):
        self.name = name
        self.printed = printed


class Overwrite:
    def __init__(self, output_name, doc_id, action, printed, count):
        self.output_name = output_name
        self.doc_id = doc_id
        self.action = action
        self.count = count
        self.printed = printed


class InfoFile:
    def __init__(self, file, processors):
        self.valid = False
        self.usedOutputs = []
        self.outputOverwrite = []
        self.cacheFiles = []
        self.redist_raw = False

        # File with complete path
        self.file = file

        # Filename without extension and without path
        self.baseFile = os.path.basename(file).replace(".yaml", "")

        if '_' not in self.baseFile:
            logger.error(self.file + " hat keinen gültigen Dateinaen")

        # Doc ID e.g. MST.A.02
        self.docId = self.baseFile.split('_')[0]

        # Title of the document
        self.docTitle = self.baseFile.split('_')[1]

        # Subfolder
        self.folder = ''.join(file.split('/')[-2:-1])

        with open(file) as yaml_file:
            yaml_data = yaml.load(yaml_file)
            self.raw_yaml = yaml_data

            if 'type' not in yaml_data:
                logger.error(self.file + " 'type' ist nicht gesetzt. Datei wird nicht verarbeitet")
                return
            self.type = yaml_data['type']

            if self.type == 'link':
                # Always use a raw redistribute for links
                self.redist_raw = True

            if self.type not in processors:
                logger.error(
                    self.file + " type '" + self.type + "'' wird nicht unterstützt. Datei wird nicht verarbeitet")
                return

            self.version = ""
            if self.type != 'link':
                if 'version' not in yaml_data:
                    logger.error(self.file + " 'version' ist nicht gesetzt. Datei wird nicht verarbeitet")
                    return
                self.version = yaml_data['version']

            self.datum = ""
            if self.type != 'link':
                if 'datum' not in yaml_data:
                    logger.error(self.file + " 'datum' ist nicht gesetzt. Datei wird nicht verarbeitet")
                    return
                self.datum = yaml_data['datum']

            self.copyright = ""
            if 'copyright' in yaml_data:
                self.copyright = yaml_data['copyright']

            self.docSubTitle = ""
            if 'subTitle' in yaml_data:
                self.docSubTitle = yaml_data['subTitle']

            self.link = ""
            if 'link' in yaml_data:
                self.link = yaml_data['link']

            self.sets = []
            if 'sets' in yaml_data and yaml_data['sets']:
                for curr_set in yaml_data['sets']:
                    self.sets.append(InfoFile.read_set_from_yaml(self, curr_set))
            else:
                logger.error(self.file + " 'sets' sind nicht gültig")

            self.variables = {}
            if 'variables' in yaml_data:
                for var in yaml_data['variables']:
                    name = var['name']
                    value = var['value']
                    self.variables[name] = value

            if 'redist_raw' in yaml_data:
                self.redist_raw = Utils.convert_yaml_bool(yaml_data['redist_raw'])

        self.valid = True

    @staticmethod
    def read_set_from_yaml(infoFile, set):
        setname = set['name']
        if not setname:
            logger.error(infoFile.file + " 'set name' ist nicht gültig")
        printed = True

        if 'print' in set:
            printed = Utils.convert_yaml_bool(set['print'])

        if infoFile.type == 'link':
            # Links are always not printed
            printed = False

        return Set(setname, printed)

    def to_string(self):
        ret = "######################################\r\n"
        ret += "File: " + self.file + "\r\n"
        ret += "Folder: " + self.folder + "\r\n"
        ret += "BaseFile: " + self.baseFile + "\r\n"
        ret += "DocId: " + self.docId + "\r\n"
        ret += "DocTitle: " + self.docTitle + "\r\n"
        ret += "Type: " + self.type + "\r\n"
        ret += "Version: " + self.version + "\r\n"
        ret += "Datum: " + self.datum + "\r\n"
        ret += "Copyright: " + self.copyright + "\r\n"
        if len(self.cacheFiles) > 0:
             ret += "Cache files: " + str(self.cacheFiles) + "\r\n"
        if len(self.sets) > 0:
            for curr_set in self.sets:
                ret += "Set: " + curr_set.name + " (Print: " + str(curr_set.printed) + ")\r\n"
        ret += "######################################"
        return ret

    def set_cache_files(self, cache_files):
        self.cacheFiles = cache_files

    def get_cache_files_for_sets(self, sets):
        ret = []
        for file in self.cacheFiles:
            if file not in ret:
                ret.append(file)
        return ret

    def copy_cache(self, output_folder, sets):
        for file in self.cacheFiles:
            subpath = output_folder + "/" + self.folder
            Utils.mkdir(subpath)
            shutil.copy(file, subpath)

    def is_printed_in_sets(self, output_name, sets):
        for ow in self.outputOverwrite:
            if ow.output_name == output_name:
                return ow.printed

        for curr_set in self.sets:
            if curr_set.name in sets:
                if curr_set.printed:
                    return True
        return False

    def is_for_sets(self, output_name, sets):
        for ow in self.outputOverwrite:
            if ow.output_name == output_name:
                return ow.action == '+'

        for curr_set in self.sets:
            if curr_set.name in sets:
                return True
        return False

    def add_output_overwrite(self, output_name, doc_id, action, printed, count):
        ow = Overwrite(output_name, doc_id, action, printed, count)
        self.outputOverwrite.append(ow)

    def add_used_output(self, output_name, printed):
        self.usedOutputs.append(Set(output_name, printed))
