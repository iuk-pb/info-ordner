import Process
import os.path
import Utils
import logging

logger = logging.getLogger(__name__)


def create_instance(info_file):
    return ProcessPdf(info_file)


class ProcessPdf(Process.Process):
    def __init__(self, info_file):
        Process.Process.__init__(self, info_file)

    def clean_workspace(self):
        Utils.rm(self.folderWork + "/overlay.pdf")
        Utils.rm(self.folderWork + "/page*.aux")
        Utils.rm(self.folderWork + "/page*.log")
        Utils.rm(self.folderWork + "/page*.pdf")
        Utils.rm(self.folderWork + "/page*.latex")

    def create_cache(self, folder_cache, folder_work, contacts):
        self.folderCache = folder_cache
        self.folderWork = folder_work

        output_file = self.folderCache + "/" + self.infoFile.baseFile + ".pdf"
        self.add_output_file(output_file)

        if not self.need_create_cache():
            # No update of the cache is required, return
            return

        raw_pdf = self.infoFile.file.replace(".yaml", ".pdf")
        self.create_pdf(raw_pdf, output_file)

    def create_pdf(self, raw_pdf, output_file):
        self.clean_workspace()

        page_count = int(os.popen("pdfinfo '" + raw_pdf + "' | grep Pages | awk '{print $2}'").read())

        self.overlay_creates_pages(page_count, raw_pdf)
        self.overlay_stamp(raw_pdf, output_file)

        self.clean_workspace()

    def overlay_stamp(self, org_pdf, pdf_target_file):
        Utils.syscall(
            "pdftk '" + org_pdf + "' multistamp " + self.folderWork + "/overlay.pdf output '" + pdf_target_file + "'")

    def overlay_creates_pages(self, page_count, raw_pdf):
        page_files = ""
        i = 1
        while i <= page_count:
            latex_file = self.folderWork + "/page" + str(i) + ".latex"
            self.overlay_create_page(latex_file, i, page_count, raw_pdf)
            page_files += " " + latex_file.replace(".latex", ".pdf")
            i += 1
            if i > 200:
                break
        Utils.syscall("pdftk " + page_files + " cat output " + self.folderWork + "/overlay.pdf")

    def overlay_create_page(self, latex_file, page_number, page_count, raw_pdf):
        page_size_width = float(os.popen("pdfinfo -f " + str(page_number) + " -l " + str(
            page_number) + " '" + raw_pdf + "' | grep 'Page.*size:' | awk '{print $4}'").read())
        page_size_height = float(os.popen("pdfinfo -f " + str(page_number) + " -l " + str(
            page_number) + " '" + raw_pdf + "' | grep 'Page.*size:' | awk '{print $6}'").read())
        page_rot = int(os.popen("pdfinfo -f " + str(page_number) + " -l " + str(
            page_number) + " '" + raw_pdf + "' | grep 'Page.*rot:' | awk '{print $4}'").read())
        if page_rot == 90 or page_rot == 270:
            tmp = page_size_width
            page_size_width = page_size_height
            page_size_height = tmp

        # TODO implement placement relative to page size
        paper_size = ""
        paper_orientation = ""
        position_copyright_left = ""
        position_copyright_top = ""
        position_copyright_width = ""
        position_vertraulich_left = ""
        position_vertraulich_top = ""
        position_vertraulich_width = ""
        position_beschriftung_left = ""
        position_beschriftung_top = ""
        position_beschriftung_width = ""
        centering_vertraulich = False
        if page_size_width >= 1188 and page_size_width <= 1192 and page_size_height >= 838 and page_size_height <= 845:
            paper_size = "A3"
            paper_orientation = "landscape"
            position_copyright_left = "1cm"
            position_copyright_top = "28.5cm"
            position_copyright_width = "10cm"
            position_vertraulich_left = "0cm"
            position_vertraulich_top = "28.5cm"
            position_vertraulich_width = "42cm"
            position_beschriftung_left = "21cm"
            position_beschriftung_top = "28.5cm"
            position_beschriftung_width = "20cm"
            centering_vertraulich = True
        elif (page_size_width >= 838 and page_size_width <= 845 and page_size_height >= 1188 and page_size_height <= 1192):
            paper_size = "A3"
            paper_orientation = "portrait"
            position_copyright_left = "1cm"
            position_copyright_top = "1cm"
            position_copyright_width = "10cm"
            position_vertraulich_left = "1.7cm"
            position_vertraulich_top = "1cm"
            position_vertraulich_width = "27cm"
            position_beschriftung_left = "1.7cm"
            position_beschriftung_top = "40.3cm"
            position_beschriftung_width = "27cm"
            centering_vertraulich = False
        elif (page_size_width >= 1678 and page_size_width <= 1682 and page_size_height >= 1166 and page_size_height <= 1170):
            # Only for Dreifachturnhalle
            paper_size = "A3"
            paper_orientation = "landscape"
            position_copyright_left = "1cm"
            position_copyright_top = "28.5cm"
            position_copyright_width = "10cm"
            position_vertraulich_left = "0cm"
            position_vertraulich_top = "28.5cm"
            position_vertraulich_width = "42cm"
            position_beschriftung_left = "21cm"
            position_beschriftung_top = "28.5cm"
            position_beschriftung_width = "20cm"
            centering_vertraulich = True
        elif (page_size_width >= 582 and page_size_width <= 596 and page_size_height >= 820 and page_size_height <= 845):
            paper_size = "A4"
            paper_orientation = "portrait"
            position_copyright_left = "1cm"
            position_copyright_top = "1cm"
            position_copyright_width = "10cm"
            position_vertraulich_left = "1cm"
            position_vertraulich_top = "1cm"
            position_vertraulich_width = "18cm"
            position_beschriftung_left = "1cm"
            position_beschriftung_top = "28.5cm"
            position_beschriftung_width = "18cm"
            centering_vertraulich = False
        elif (page_size_width >= 820 and page_size_width <= 845 and page_size_height >= 582 and page_size_height <= 596):
            paper_size = "A4"
            paper_orientation = "landscape"
            position_copyright_left = "1cm"
            position_copyright_top = "0.8cm"
            position_copyright_width = "10cm"
            position_vertraulich_left = "13.5cm"
            position_vertraulich_top = "0.8cm"
            position_vertraulich_width = "15cm"
            position_beschriftung_left = "1cm"
            position_beschriftung_top = "20cm"
            position_beschriftung_width = "27.5cm"
            centering_vertraulich = False
        else:
            logger.error("Unkown page size: " + str(page_size_width) + "x" + str(page_size_height))
            return

        with open(latex_file, 'w') as file:
            file.write('\\documentclass[\n')
            file.write('ngerman,\n')
            file.write('headinclude=false,\n')
            file.write('footinclude=false,\n')
            file.write('paper=' + paper_size + ',\n')
            file.write('paper=' + paper_orientation + ',\n')
            file.write('pagesize\n')
            file.write(']{scrartcl}\n')
            file.write('\\usepackage{colordvi,epsf}\n')
            file.write('\\usepackage[pdftex,usenames,dvipsnames]{color}\n')
            file.write('\\usepackage[pdftex]{graphicx}\n')
            file.write('\\usepackage[absolute,overlay]{textpos}\n')
            file.write('\\usepackage{xcolor}\n')
            file.write('\\usepackage[utf8]{inputenc}\n')
            file.write('\n')
            file.write('\\pagenumbering{gobble}\n')
            file.write('\n')
            file.write('\\begin{document}\n')
            file.write('\n')
            if len(self.infoFile.copyright) > 0:
                file.write(
                    '\\begin{textblock*}{' + position_copyright_width + '}(' + position_copyright_left + ',' + position_copyright_top + ')\n')
                file.write('\\colorbox{gray!30}{' + self.infoFile.copyright + '}\n')
                file.write('\\end{textblock*}\n')
                file.write('\n')

            file.write(
                '\\begin{textblock*}{' + position_vertraulich_width + '}(' + position_vertraulich_left + ',' + position_vertraulich_top + ')\n')
            if centering_vertraulich:
                file.write('\\centering\n')
            else:
                file.write('\\raggedleft\n')
            file.write('\\colorbox{gray!30}{Vertraulich - Nur f\\"ur den Dienstgebrauch}\n')
            file.write('\\end{textblock*}\n')
            file.write('\n')
            file.write(
                '\\begin{textblock*}{' + position_beschriftung_width + '}(' + position_beschriftung_left + ',' + position_beschriftung_top + ')\n')
            file.write('\\raggedleft\n')
            file.write(
                '\\colorbox{gray!30}{' + self.infoFile.docTitle + ' - Version ' + self.infoFile.version + ' - ' + self.infoFile.datum + ' - Seite ' + str(
                    page_number) + '/' + str(page_count) + ' - ' + self.infoFile.docId + '}\n')
            file.write('\\end{textblock*}\n')
            file.write('\n')
            file.write('\\end{document}\n')

        Utils.syscall("pdflatex -output-directory=" + self.folderWork + " " + latex_file)
