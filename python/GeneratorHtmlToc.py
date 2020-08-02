import os.path
import time
import Generator


def create_instance(output_name, parameters, entries, sets, folder_work, folder_output, input_folders):
    return GeneratorPdfToc(output_name, parameters, entries, sets, folder_work, folder_output, input_folders)


class GeneratorPdfToc(Generator.Generator):
    def __init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders):
        Generator.Generator.__init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders)

        self.docId = ""
        if 'docId' in self.parameters:
            self.docId = self.parameters['docId']

        self.docTitle = ""
        if 'docTitle' in self.parameters:
            self.docTitle = self.parameters['docTitle'].replace('%OUTPUTNAME%', output_name)

        self.copyright = ""
        if 'copyright' in self.parameters:
            self.copyright = self.parameters['copyright']

        self.datum = time.strftime("%d.%m.%Y")

    def generate(self):
        with open(self.folder_output + "/index.html", 'w') as file:
            with open(os.path.dirname(os.path.abspath(__file__)) + "/htmlToc_prefix.html", 'r') as prefix:
                file.write(prefix.read())

            is_first = True
            last_category = ""
            for entry in self.entries:
                if entry.folder != last_category:
                    if not is_first:
                        file.write("</table>")
                    is_first = False
                    file.write("<table class=\"entries\">")
                    self.toc_generate_category_html(file, entry.folder)
                    last_category = entry.folder

                link = ""
                if entry.type == 'link':
                    link = entry.link
                else:
                    if len(entry.cacheFiles) > 0:
                        link = entry.folder + "/" + os.path.basename(entry.cacheFiles[0])

                self.toc_generate_entry_html(file, entry.docTitle, entry.docSubTitle, entry.datum, entry.version,
                                             entry.docId, link)

            file.write("</table>\n")

            with open(os.path.dirname(os.path.abspath(__file__)) + "/htmlToc_postfix.html", 'r') as postfix:
                file.write(postfix.read())

    def toc_generate_category_html(self, file, name):
        file.write("<tr><th colspan=\"3\">" + name + "</th></tr>\n")

    def toc_generate_entry_html(self, file, title, subtitle, datum, version, doc_id, href):
        file.write("<tr>")
        link = "<a href=\"" + href + "\" target=\"_blank\">"

        if len(subtitle) > 0:
            file.write("<td>" + link + "<b>" + title + "</b><br/>" + subtitle + "</a></td>\n")
        else:
            file.write("<td>" + link + "<b>" + title + "</b></a></td>\n")

        if len(version) > 0 and len(datum) > 0:
            file.write("<td>" + link + "Version: " + version + "<br/>Datum: " + datum + "</a></td>\n")
        elif len(version):
            file.write("<td>" + link + "Version: " + version + "<br/></a></td>\n")
        elif len(datum):
            file.write("<td>" + link + "<br/>Datum: " + datum + "</a></td>\n")
        else:
            file.write("<td>" + link + "<br/></a></td>\n")

        file.write("<td>" + link + "" + doc_id + "</a></td>\n")

        file.write("</tr>\n")
