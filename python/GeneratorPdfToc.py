import os.path
import time
import shutil
import Generator
import Utils
import logging

TOC_HEIGHT_CATEGORY = 10
TOC_X_CATEGORY = 10
TOC_X_ENTRY = 20
TOC_ENTRY_HEIGHT_SINGLE_LINE = 5
TOC_ENTRY_HEIGHT_DOUBLE_LINE = TOC_ENTRY_HEIGHT_SINGLE_LINE * 2
TOC_TOTAL_WIDTH = 190
TOC_TITLE_WIDTH = 88
TOC_VERSION_WIDTH = 36
TOC_ID_WIDTH = TOC_TOTAL_WIDTH - (TOC_X_ENTRY - TOC_X_CATEGORY) - TOC_TITLE_WIDTH - TOC_VERSION_WIDTH - 2

# Set logging settings #################################################################################################

logger = logging.getLogger(__name__)


def create_instance(output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables):
    return GeneratorPdfToc(output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables)


class GeneratorPdfToc(Generator.Generator):
    def __init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables):
        Generator.Generator.__init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders, contacts, variables)

        self.latexFile = None

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
        toc_file = self.folder_work + "/toc.latex"
        pdf_file = self.folder_output + "/" + self.docId + "_" + self.docTitle + ".pdf"

        with open(toc_file, 'w') as self.latexFile:
            self.latex_toc_add_header()

            self.generate_toc_data(self.entries)

            self.latex_toc_end_tikz()
            self.latex_toc_add_footer()
        self.latexFile = None

        Utils.syscall("pdflatex -output-directory=" + self.folder_work + " " + toc_file)
        Utils.syscall("pdflatex -output-directory=" + self.folder_work + " " + toc_file)

        shutil.copy(toc_file.replace(".latex", ".pdf"), pdf_file)

    def generate_toc_data(self, entries):

        y = 15

        self.latex_toc_add_page()

        last_category = ""
        count_in_category = 0
        for entry in entries:
            if not entry.type == 'link':
                logger.debug("Erzeuge TOC Eintrag für " + entry.docId)
                if y > 260:
                    # Make a page break
                    self.latex_toc_end_tikz()
                    self.latex_toc_add_break()
                    self.latex_toc_add_page()
                    last_category = ""
                    y = 15

                if entry.folder != last_category:
                    if y > 15:
                        y += TOC_HEIGHT_CATEGORY
                    self.toc_generate_category(entry.folder, y)
                    y += TOC_HEIGHT_CATEGORY
                    last_category = entry.folder
                    count_in_category = 0

                not_printed = not entry.is_printed_in_sets(self.output_name, self.sets)
                self.toc_generate_entry(y, entry.docTitle, entry.docSubTitle, entry.datum, entry.version, entry.docId,
                                        count_in_category, not_printed)
                y += TOC_ENTRY_HEIGHT_DOUBLE_LINE
                count_in_category += 1

    def latex_toc_add_header(self):
        self.latexFile.write('\\documentclass[\n')
        self.latexFile.write('ngerman,\n')
        self.latexFile.write('headinclude=false,\n')
        self.latexFile.write('footinclude=false,\n')
        self.latexFile.write('paper=A4,\n')
        self.latexFile.write('paper=portrait,\n')
        self.latexFile.write('pagesize\n')
        self.latexFile.write(']{scrartcl}\n')
        self.latexFile.write('\\usepackage{colordvi,epsf}\n')
        self.latexFile.write('\\usepackage[pdftex,usenames,dvipsnames]{color}\n')
        self.latexFile.write('\\usepackage[pdftex]{graphicx}\n')
        self.latexFile.write('\\usepackage[absolute,overlay]{textpos}\n')
        self.latexFile.write('\\usepackage{xcolor}\n')
        self.latexFile.write('\\usepackage[utf8]{inputenc}\n')
        self.latexFile.write('\\usepackage{picture}\n')
        self.latexFile.write('\\usepackage{tikz}\n')
        self.latexFile.write('\\usepackage{lastpage}\n')
        self.latexFile.write('\\definecolor{ral3001}{cmyk}{0, 0.77, 0.77, 0.39}\n')
        self.latexFile.write('\\definecolor{backgroundGray}{cmyk}{0, 0, 0, 0.2}\n')
        self.latexFile.write('\\setkeys{Gin}{keepaspectratio}\n')
        self.latexFile.write('\\begin{document}\n')

    def latex_toc_add_footer(self):
        self.latexFile.write('\\end{document}\n')

    def latex_toc_add_page(self):
        self.latexFile.write('\\thispagestyle{empty}\n')
        self.latexFile.write('\\begin{textblock*}{10cm}(0.65cm,0.9cm)\n')
        self.latexFile.write('\\colorbox{gray!30}{' + self.copyright + '}\n')
        self.latexFile.write('\\end{textblock*}\n')
        self.latexFile.write('\n')
        self.latexFile.write('\\begin{textblock*}{19cm}(1cm,0.9cm)\n')
        self.latexFile.write('\\raggedleft\n')
        self.latexFile.write('\\colorbox{gray!30}{Vertraulich - Nur f\\"ur den Dienstgebrauch}\n')
        self.latexFile.write('\\end{textblock*}\n')
        self.latexFile.write('\n')
        self.latexFile.write('\\begin{textblock*}{19cm}(1cm,28.5cm)\n')
        self.latexFile.write('\\raggedleft\n')
        self.latexFile.write(
            '\\colorbox{gray!30}{' + Utils.latex_escape(self.docTitle) + ' - Datum ' + self.datum +
            ' - Seite \\thepage/\\pageref{LastPage}  - ' + self.docId + '}\n')
        self.latexFile.write('\\end{textblock*}\n')
        self.latexFile.write('\\begin{tikzpicture}[remember picture,overlay, anchor = north west]\n')

    def latex_toc_end_tikz(self):
        self.latexFile.write('\\end{tikzpicture}\n')

    def latex_toc_add_break(self):
        self.latexFile.write('\\newpage\n')

    def toc_generate_category(self, name, y_position):
        self.latexFile.write('\\node[fill=ral3001,draw=black,anchor=north west, minimum width=' + str(
            TOC_TOTAL_WIDTH) + 'mm,minimum height=' + str(TOC_HEIGHT_CATEGORY) + 'mm]\n')
        self.latexFile.write(
            'at ([xshift=' + str(TOC_X_CATEGORY) + 'mm,yshift=-' + str(y_position) + 'mm]current page.north west) {\n')
        self.latexFile.write('\\fontsize{18}{18} \\selectfont\n')
        self.latexFile.write('\\color{white}\\textbf{' + name.replace('_', '\\_') + '}\n')
        self.latexFile.write('};\n')

    def latex_toc_create_text(self, x_position, y_position, width, height, text, align):
        self.latexFile.write('\\node[anchor=north west, minimum width=' + str(width) + 'mm,minimum height=' + str(
            height) + 'mm, text width=' + str(width) + 'mm,align=' + align + ']\n')
        self.latexFile.write(
            'at ([xshift=' + str(x_position) + 'mm,yshift=-' + str(y_position) + 'mm]current page.north west) {\n')
        self.latexFile.write(Utils.latex_escape(text) + '\n')
        self.latexFile.write('};\n')

    def latex_toc_create_text_bold(self, x_position, y_position, width, height, text, align):
        self.latexFile.write('\\node[anchor=north west, minimum width=' + str(width) + 'mm,minimum height=' + str(
            height) + 'mm, text width=' + str(width) + 'mm,align=' + align + ']\n')
        self.latexFile.write(
            'at ([xshift=' + str(x_position) + 'mm,yshift=-' + str(y_position) + 'mm]current page.north west) {\n')
        self.latexFile.write('\\fontsize{14}{14} \\selectfont\n')
        self.latexFile.write('\\textbf{' + Utils.latex_escape(text) + '}\n')
        self.latexFile.write('};\n')

    def toc_generate_entry(self, y_position, title, subtitle, datum, version, doc_id, count_in_category, not_printed):

        if len(datum) > 10:
            datum = datum[:7] + '...'

        if count_in_category % 2 == 1:
            self.latexFile.write('\\node[fill=backgroundGray,anchor=north west, minimum width=' + str(
                TOC_TOTAL_WIDTH - TOC_X_CATEGORY) + 'mm, minimum height=' + str(TOC_ENTRY_HEIGHT_DOUBLE_LINE) + 'mm]\n')
            self.latexFile.write(
                'at ([xshift=' + str(TOC_X_ENTRY) + 'mm,yshift=-' + str(y_position) + 'mm]current page.north west) {\n')
            self.latexFile.write('};\n')

        self.latexFile.write('\\draw ([yshift=-' + str(y_position + TOC_ENTRY_HEIGHT_DOUBLE_LINE) + 'mm,xshift=' + str(
            TOC_X_ENTRY) + 'mm]current page.north west) -- ([yshift=-' + str(
            y_position + TOC_ENTRY_HEIGHT_DOUBLE_LINE) + 'mm,xshift=-1cm]current page.north east);\n')

        if len(subtitle) > 0:
            self.latex_toc_create_text(TOC_X_ENTRY, y_position, TOC_TITLE_WIDTH, TOC_ENTRY_HEIGHT_SINGLE_LINE, title,
                                       'left')

            self.latex_toc_create_text(TOC_X_ENTRY, y_position + TOC_ENTRY_HEIGHT_SINGLE_LINE, TOC_TITLE_WIDTH,
                                       TOC_ENTRY_HEIGHT_SINGLE_LINE, subtitle, 'left')
        else:
            self.latex_toc_create_text(TOC_X_ENTRY, y_position, TOC_TITLE_WIDTH, TOC_ENTRY_HEIGHT_DOUBLE_LINE, title,
                                       'left')

        if len(version) > 0:
            self.latex_toc_create_text(TOC_X_ENTRY + TOC_TITLE_WIDTH, y_position, TOC_VERSION_WIDTH,
                                       TOC_ENTRY_HEIGHT_SINGLE_LINE, "Version: " + version, 'left')

        if len(datum) > 0:
            self.latex_toc_create_text(TOC_X_ENTRY + TOC_TITLE_WIDTH, y_position + TOC_ENTRY_HEIGHT_SINGLE_LINE,
                                       TOC_VERSION_WIDTH, TOC_ENTRY_HEIGHT_SINGLE_LINE, "Datum: " + datum, 'left')

        if not_printed:
            self.latex_toc_create_text(TOC_X_ENTRY + TOC_TITLE_WIDTH + TOC_VERSION_WIDTH, y_position, TOC_ID_WIDTH,
                                       TOC_ENTRY_HEIGHT_DOUBLE_LINE, doc_id + "*", 'right')
        else:
            self.latex_toc_create_text_bold(TOC_X_ENTRY + TOC_TITLE_WIDTH + TOC_VERSION_WIDTH, y_position, TOC_ID_WIDTH,
                                            TOC_ENTRY_HEIGHT_DOUBLE_LINE, doc_id, 'right')
