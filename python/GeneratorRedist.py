import Generator
import Utils
from ruamel.yaml import YAML
import glob
import shutil

def create_instance(output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables):
    return GeneratorRedist(output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables)


class GeneratorRedist(Generator.Generator):
    def __init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables):
        Generator.Generator.__init__(self, output_name, parameters, entries, sets, folder_work, folder_output,
                                     input_folders, contacts, variables)

    def generate(self):
        for entry in self.entries:
            Utils.mkdir(self.folder_output + '/' + entry.folder)
            with open(self.folder_output + '/' + entry.folder + '/' + entry.baseFile + '.yaml', 'w') as file:
                if entry.redist_raw:
                    yamldata = entry.raw_yaml.copy()
                    if 'sets' in yamldata:
                        del yamldata['sets']

                    yaml = YAML()
                    yaml.dump(yamldata, file)

                    raw_without_extension = entry.file.replace(".yaml", ".*")
                    additional_files = glob.glob(raw_without_extension)
                    for addfile in additional_files:
                        if not addfile.endswith(".yaml"):
                            subpath = self.folder_output + '/' + entry.folder
                            print("------------------Copy file " + addfile + " to " + subpath)
                            Utils.mkdir(subpath)
                            shutil.copy(addfile, subpath)
                else:
                    file.write("type: copy\r\n")
                    file.write("version: \"" + entry.version + "\"\r\n")
                    file.write("datum: \"" + entry.datum + "\"\r\n")

                # print(entry.to_string())
                # print('####')
                # print(self.sets)
                # print('----------')

                file.write("sets:\r\n")
                for curr_set in entry.sets:
                    if curr_set.name in self.sets:
                        file.write(" - name: " + curr_set.name + "\r\n")
                        if curr_set.printed:
                            file.write("   print: y\r\n")
                        else:
                            file.write("   print: n\r\n")

        self.generate_contacts()

    def generate_contacts(self):
        Utils.mkdir(self.folder_output + '/_Kontakte')
        self.contacts.write_file(self.folder_output + '/_Kontakte/kontakte.vcf', self.sets)
