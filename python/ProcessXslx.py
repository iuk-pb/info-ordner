import ProcessPdf
import shutil
import Utils


def create_instance(info_file):
    return ProcessXslx(info_file)


class ProcessXslx(ProcessPdf.ProcessPdf):
    def __init__(self, info_file):
        ProcessPdf.ProcessPdf.__init__(self, info_file)

    def create_cache(self, folder_cache, folder_work, contacts):
        self.folderCache = folder_cache
        self.folderWork = folder_work

        output_file = self.folderCache + "/" + self.infoFile.baseFile + ".pdf"
        self.add_output_file(output_file)

        if not self.need_create_cache():
            # No update of the cache is required, return
            return

        org_file = self.infoFile.file.replace(".yaml", ".xlsx")
        tmp_ini = self.folderWork + "/xlsx.ini"
        tmp_pdf = self.folderWork + "/xslx.pdf"
        tmp_xslx = self.folderWork + "/xslx.xslx"

        shutil.copy(org_file, tmp_xslx)

        with open(tmp_ini, 'w') as file:
            file.write('[pdf files]\n')
            file.write('AppFile=' + tmp_xslx + '\n')
            file.write('PdfFile=' + tmp_pdf + '\n')

        Utils.syscall('planmaker18 -pdf:"' + tmp_ini + '"')

        self.create_pdf(tmp_pdf, output_file)
