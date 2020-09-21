import Generator
import Utils


def create_instance(output_name, parameters, entries, sets, folder_work, folder_output, input_folders):
    return GeneratorRedist(output_name, parameters, entries, sets, folder_work, folder_output, input_folders)


class GeneratorRedist(Generator.Generator):
    def __init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders):
        Generator.Generator.__init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders)

    def generate(self):
        for entry in self.entries:
            Utils.mkdir(self.folder_output + '/' + entry.folder)
            with open(self.folder_output + '/' + entry.folder + '/' + entry.baseFile + '.yaml', 'w') as file:
                if entry.type == 'link':
                    file.write("type: link\r\n")
                    file.write("link: " + entry.link + "\r\n")
                else:
                    file.write("type: copy\r\n")
                    file.write("version: \"" + entry.version + "\"\r\n")
                    file.write("datum: \"" + entry.datum + "\"\r\n")
                file.write("sets:\r\n")

                # print(entry.to_string())
                # print('####')
                # print(self.sets)
                # print('----------')

                for curr_set in entry.sets:
                    if curr_set.name in self.sets:
                        file.write(" - name: " + curr_set.name + "\r\n")
                        if curr_set.printed:
                            file.write("   print: y\r\n")
                        else:
                            file.write("   print: n\r\n")
