import os.path
import time
import Generator
import os
import shutil

def create_instance(output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables):
    return GeneratorPdfToc(output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables)


class GeneratorPdfToc(Generator.Generator):
    def __init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables):
        Generator.Generator.__init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables)

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

    def copytree(self, src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)

    def write_header(self, file):
        file.write("<div id=\"header\">\n")
        file.write("<span id=\"header_text\">Info-Ordner für " + self.output_name + "</span><br/>\n")
        file.write("<span id=\"header_stand\">Stand: " + self.datum + "</span>\n")
        file.write("<a href=\"javascript:UpdateApp();\">(Aktualisieren)</a>\n")
        file.write("</div>\n")
        file.write("<div id=\"search\"><input  type=\"text\" id=\"myInput\" onkeyup=\"myFunction()\" placeholder=\"Suche ...\" title=\"Zur Suche tippen\"></div>\n\n")

    def generate(self):
        self.copytree(os.path.dirname(os.path.abspath(__file__)) + "/htmlToc_Files", self.folder_output)
        with open(self.folder_output + "/index.html", 'w') as file:
            with open(os.path.dirname(os.path.abspath(__file__)) + "/htmlToc_prefix.html", 'r') as prefix:
                file.write(prefix.read())

            self.write_header(file)

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
                    cacheFilesForSets = entry.get_cache_files_for_sets(self.sets)
                    if len(cacheFilesForSets) > 0:
                        link = entry.folder + "/" + os.path.basename(cacheFilesForSets[0])

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
