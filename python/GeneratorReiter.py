import os.path
import time
import shutil
import Generator
import Utils


def create_instance(output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables):
    return GeneratorPdfToc(output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables)


class GeneratorPdfToc(Generator.Generator):
    def __init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables):
        Generator.Generator.__init__(self, output_name, parameters, entries, sets, folder_work, folder_output,
                                     input_folders, contacts, variables)

        self.size = ""
        if 'size' in self.parameters:
            self.size = self.parameters['size']

        self.printEntries = True
        if 'einzeln' in self.parameters:
            self.printEntries = Utils.convert_yaml_bool(self.parameters['einzeln'])

        self.printFolder = True
        if 'ordner' in self.parameters:
            self.printFolder = Utils.convert_yaml_bool(self.parameters['ordner'])

    def generate(self):
        self.reiter_create_with_size(self.entries, self.folder_output, self.size)

    def reiter_create_with_size(self, entries, output_folder, size):
        latex_file = self.folder_work + "/Reiter" + size + ".latex"

        with open(latex_file, 'w') as file:
            self.reiter_add_header(file, size)

            counter = 0
            add_new_page = False
            endtikz = False
            last_folder = ""

            for entry in entries:
                if not entry.type == 'link':
                    if self.printFolder:
                        if entry.folder != last_folder:
                            if counter % 2 == 0:
                                if add_new_page:
                                    self.reiter_add_break(file)
                                    add_new_page = False
                                self.reiter_add_page(file)
                                if size == 'A3':
                                    self.reiter_add_a3(file)
                                    self.reiter_a3_field_left(file, entry.folder, "")
                                else:
                                    self.reiter_add_a4(file)
                                    self.reiter_a4_field_left(file, entry.folder, "")
                                endtikz = False
                            else:
                                if size == 'A3':
                                    self.reiter_a3_field_right(file, entry.folder, "")
                                else:
                                    self.reiter_a4_field_right(file, entry.folder, "")
                                self.reiter_end_tikz(file)
                                endtikz = True
                                add_new_page = True
                            counter += 1
                            last_folder = entry.folder

                    if self.printEntries:
                        if counter % 2 == 0:
                            if add_new_page:
                                self.reiter_add_break(file)
                                add_new_page = False
                            self.reiter_add_page(file)
                            if size == 'A3':
                                self.reiter_add_a3(file)
                                self.reiter_a3_field_left(file, entry.docId, entry.docTitle)
                            else:
                                self.reiter_add_a4(file)
                                self.reiter_a4_field_left(file, entry.docId, entry.docTitle)
                            endtikz = False
                        else:
                            if size == 'A3':
                                self.reiter_a3_field_right(file, entry.docId, entry.docTitle)
                            else:
                                self.reiter_a4_field_right(file, entry.docId, entry.docTitle)
                            self.reiter_end_tikz(file)
                            endtikz = True
                            add_new_page = True
                        counter += 1

            if not endtikz:
                self.reiter_end_tikz(file)
            self.reiter_add_footer(file)

        Utils.syscall("pdflatex -output-directory=" + self.folder_work + " " + latex_file)
        Utils.syscall("pdflatex -output-directory=" + self.folder_work + " " + latex_file)
        shutil.copy(latex_file.replace(".latex", ".pdf"), output_folder)

    def reiter_add_header(self, file, page_size):
        file.write('\\documentclass[\n')
        file.write('ngerman,\n')
        file.write('headinclude=false,\n')
        file.write('footinclude=false,\n')
        file.write('paper=' + page_size + ',\n')
        file.write('paper=portrait,\n')
        file.write('pagesize\n')
        file.write(']{scrartcl}\n')
        file.write('\\usepackage{colordvi,epsf}\n')
        file.write('\\usepackage[pdftex,usenames,dvipsnames]{color}\n')
        file.write('\\usepackage[pdftex]{graphicx}\n')
        file.write('\\usepackage[absolute,overlay]{textpos}\n')
        file.write('\\usepackage{xcolor}\n')
        file.write('\\usepackage[utf8]{inputenc}\n')
        file.write('\\usepackage{picture}\n')
        file.write('\\usepackage{tikz}\n')
        file.write('\\pagenumbering{gobble}\n')
        file.write('\\setkeys{Gin}{keepaspectratio}\n')
        file.write('\\begin{document}\n')

    def reiter_add_footer(self, file):
        file.write('\\end{document}\n')

    def reiter_add_page(self, file):
        file.write('\\thispagestyle{empty}\n')
        file.write('\\begin{tikzpicture}[remember picture,overlay, anchor = north west]\n')

    def reiter_end_tikz(self, file):
        file.write('\\end{tikzpicture}\n')

    def reiter_add_break(self, file):
        file.write('\\newpage\n')

    def reiter_a3_field_left(self, file, doc_id, description):
        if len(description) > 0:
            self.reiter_add_text_field(file, '1.3', '14.85', '1.0', '13.5', '-28.9', '-7.425', description)
        if len(doc_id) > 0:
            self.reiter_add_text_field(file, '1.3', '14.85', '1.0', '13.5', '-30.2', '-7.425', doc_id)

    def reiter_a3_field_right(self, file, doc_id, description):
        if len(description) > 0:
            self.reiter_add_text_field(file, '1.3', '14.85', '1.0', '13.5', '-28.9', '7.425', description)
        if len(doc_id) > 0:
            self.reiter_add_text_field(file, '1.3', '14.85', '1.0', '13.5', '-30.2', '7.425', doc_id)

    def reiter_a4_field_left(self, file, doc_id, description):
        if len(description) > 0:
            self.reiter_add_text_field(file, '1.3', '10.5', '1.0', '9', '-19.9', '-5.25', description)
        if len(doc_id) > 0:
            self.reiter_add_text_field(file, '1.3', '10.5', '1.0', '9', '-21.2', '-5.25', doc_id)

    def reiter_a4_field_right(self, file, doc_id, description):
        if len(description) > 0:
            self.reiter_add_text_field(file, '1.3', '10.5', '1.0', '9', '-19.9', '5.25', description)
        if len(doc_id) > 0:
            self.reiter_add_text_field(file, '1.3', '10.5', '1.0', '9', '-21.2', '5.25', doc_id)

    def reiter_add_a3(self, file):
        file.write(
            '\\draw ([yshift=0cm,xshift=7.425cm]current page.north west) -- ([yshift=-1.5cm,xshift=7.425cm]current page.north west);\n')
        file.write(
            '\\draw ([yshift=0cm,xshift=22.275cm]current page.north west) -- ([yshift=-1.5cm,xshift=22.275cm]current page.north west);\n')
        file.write(
            '\\draw[loosely dotted] ([yshift=0cm,xshift=14.85cm]current page.north west) -- ([yshift=-1cm,xshift=14.85cm]current page.north west);\n')
        file.write(
            '\\draw[loosely dotted] ([yshift=-32.2cm,xshift=14.85cm]current page.north west) -- ([yshift=-33cm,xshift=14.85cm]current page.north west);\n')
        file.write(
            '\\draw[loosely dotted] ([yshift=-32.2cm,xshift=0cm]current page.north west) -- ([yshift=-32.2cm,xshift=1cm]current page.north west);\n')
        file.write(
            '\\draw[loosely dotted] ([yshift=-32.2cm,xshift=28.7cm]current page.north west) -- ([yshift=-32.2cm,xshift=29.7cm]current page.north west);\n')
        self.reiter_add_comment(file, '8', 'Mittig lang schnitt bei 14,85 cm')
        self.reiter_add_comment(file, '7', 'Rest abschneiden von 10,0 cm')
        self.reiter_add_comment(file, '6', 'Lochung din A6')

    def reiter_add_a4(self, file):
        file.write(
            '\\draw ([yshift=0cm,xshift=5.25cm]current page.north west) -- ([yshift=-1.5cm,xshift=5.25cm]current page.north west);\n')
        file.write(
            '\\draw ([yshift=0cm,xshift=15.75cm]current page.north west) -- ([yshift=-1.5cm,xshift=15.75cm]current page.north west);\n')
        file.write(
            '\\draw[loosely dotted] ([yshift=0cm,xshift=10.5cm]current page.north west) -- ([yshift=-1cm,xshift=10.5cm]current page.north west);\n')
        file.write(
            '\\draw[loosely dotted] ([yshift=-23.2cm,xshift=10.5cm]current page.north west) -- ([yshift=-24cm,xshift=10.5cm]current page.north west);\n')
        file.write(
            '\\draw[loosely dotted] ([yshift=-23.2cm,xshift=0cm]current page.north west) -- ([yshift=-23.2cm,xshift=1cm]current page.north west);\n')
        file.write(
            '\\draw[loosely dotted] ([yshift=-23.2cm,xshift=20cm]current page.north west) -- ([yshift=-23.2cm,xshift=21cm]current page.north west);\n')
        self.reiter_add_comment(file, '4', 'Mittig lang schnitt bei 10,5 cm')
        self.reiter_add_comment(file, '3', 'Abschneiden in Längsrichtung bei 23cm')

    def reiter_add_comment(self, file, position_from_bottom, comment):
        file.write('\\node[anchor=south, minimum width=\\paperwidth/2]\n')
        file.write('at ([yshift=' + position_from_bottom + 'cm]current page.south) {\n')
        file.write('\\begin{tabular}{r l}\n')
        file.write(comment + '\n')
        file.write('\\end{tabular}\n')
        file.write('};\n')

    def reiter_add_text_field(self, file, height, width, inner_height, inner_width, yshift, xshift, text):
        file.write('\\node[anchor=north,minimum height=' + height + 'cm, minimum width=' + width + 'cm]\n')
        file.write('at ([yshift=' + yshift + 'cm,xshift=' + xshift + 'cm]current page.north) {\n')
        file.write('\\centering\n')
        file.write('\\fontsize{32}{32} \\selectfont\n')
        file.write('\\resizebox{' + inner_width + 'cm}{' + inner_height + 'cm}{\\textbf{' + Utils.latex_escape(text) + '}}\n')
        file.write('};\n')
