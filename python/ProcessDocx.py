import ProcessPdf
import Utils

def create_instance(info_file):
    return ProcessDocx(info_file)


class ProcessDocx(ProcessPdf.ProcessPdf):
    def __init__(self, info_file):
        ProcessPdf.ProcessPdf.__init__(self, info_file)

    def create_cache(self, folder_cache, folder_work):
        self.folderCache = folder_cache
        self.folderWork = folder_work

        output_file = self.folderCache + "/" + self.infoFile.baseFile + ".pdf"
        self.add_output_file(output_file)

        if not self.need_create_cache():
            # No update of the cache is required, return
            return

        org_file = self.infoFile.file.replace(".yaml", ".docx")
        tmp_ini = self.folderWork + "/docx.ini"
        tmp_pdf = self.folderWork + "/docx.pdf"
        tmp_docx = self.folderWork + "/docx.docx"

        Utils.syscall("cp '" + org_file + "' " + tmp_docx)

        with open(tmp_ini, 'w') as file:
            file.write('[pdf files]\n')
            file.write('AppFile=' + tmp_docx + '\n')
            file.write('PdfFile=' + tmp_pdf + '\n')

        Utils.syscall('textmaker18 -pdf:"' + tmp_ini + '"')

        self.create_pdf(tmp_pdf, output_file)
