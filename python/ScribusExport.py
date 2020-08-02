# -*- coding: utf-8 -*-

sla_file = os.environ['INFOFILE_SLA_IN']
output_file = os.environ['INFOFILE_SLA_OUT']

scribus.openDoc(sla_file)
pdf = scribus.PDFfile()
pdf.file = output_file
pdf.save()
scribus.closeDoc()
