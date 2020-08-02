import Generator
import yaml
import os.path
import logging
import Utils
import shutil
import time


ACTION_ADD = 'add'
ACTION_REMOVE = 'remove'
ACTION_CHANGE = 'change'

REASON_ADD = "Wurde hinzugefügt"
REASON_REMOVE = "Wurde entfernt"
REASON_CHANGE_TITLE = "Titel wurde geändert"
REASON_CHANGE_VERSIONDATUM = "Wurde aktualisiert"
REASON_NOT_PRINTED_ANYMORE = "Wird nicht mehr gedruckt vorgehalten"
REASON_PRINTED_NOW = "Wird jetzt gedruckt vorgehalten"

CHECKLIST_REMOVE_PRINTED = ['Entferne Dokument', 'Entferne Reiter']
CHECKLIST_ADD_PRINTED = ['Drucke Dokument', 'Drucke Reiter', 'Sortiere Reiter ein', 'Sortiere Dokument ein']
CHECKLIST_CHANGE_TITLE = ['Drucke Reiter', 'Sortiere Reiter ein']
CHECKLIST_CHANGE_VERSIONDATUM = ['Drucke Dokument', 'Entferne altes Dokument', 'Sortiere neues Dokument ein']

# Set logging settings #################################################################################################

logger = logging.getLogger(__name__)


def create_instance(output_name, parameters, entries, sets, folder_work, folder_output, input_folders):
    return GeneratorHistory(output_name, parameters, entries, sets, folder_work, folder_output, input_folders)


def get_entry_by_docid(entry, entries):
    for curr_entry in entries:
        if entry.docId == curr_entry.docId:
            return curr_entry
    return None


def is_docid_in_entries(entry, entries):
    if get_entry_by_docid(entry, entries) is None:
        return False
    return True


class HistoryEntry:
    def __init__(self, dict_entry):
        self.docId = dict_entry['docId']
        self.docTitle = dict_entry['docTitle']
        self.datum = dict_entry['datum']
        self.version = dict_entry['version']
        self.wasPrinted = dict_entry['wasPrinted']


class HistoryItem:
    def __init__(self):
        self.action = ''
        self.doc_id = ''
        self.old_doc_title = ''
        self.old_version = ''
        self.old_datum = ''
        self.old_was_printed = False
        self.new_doc_title = ''
        self.new_version = ''
        self.new_datum = ''
        self.new_is_printed = False
        self.changes = []
        self.checklist = []
        self.reason = []


class GeneratorHistory(Generator.Generator):
    def __init__(self, output_name, parameters, entries, sets, folder_work, folder_output, input_folders):
        Generator.Generator.__init__(self, output_name, parameters, entries, sets, folder_work, folder_output,
                                     input_folders)
        self.current_state = {}
        self.current_state['entries'] = []
        self.last_entries = []

        self.latexFile = None
        self.historyItems = []

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
        self.read_last_entries()

        for entry in self.entries:
            is_printed = entry.is_printed_in_sets(self.sets)
            self.add_current_state(entry, is_printed)

            last_entry = get_entry_by_docid(entry, self.last_entries)
            if last_entry is None:
                self.add_history_item(ACTION_ADD, entry.docId, '', '', '', False, entry.docTitle, entry.version,
                                      entry.datum, is_printed)
                continue

            changed = False
            if is_printed != last_entry.wasPrinted:
                # Print was changed
                changed = True

            if entry.docTitle != last_entry.docTitle:
                # Change of title, reiter may be changed
                changed = True

            if entry.version != last_entry.version or entry.datum != last_entry.datum:
                # Datum or version changed
                changed = True

            if changed:
                self.add_history_item(ACTION_CHANGE, entry.docId, last_entry.docTitle, last_entry.version,
                                      last_entry.datum, last_entry.wasPrinted,
                                      entry.docTitle, entry.version, entry.datum, is_printed)

        # Check if all last entries exists in current entries
        for last_entry in self.last_entries:
            if not is_docid_in_entries(last_entry, self.entries):
                self.add_history_item(ACTION_REMOVE, last_entry.docId, last_entry.docTitle, last_entry.version,
                                      last_entry.datum, last_entry.wasPrinted, '', '', '', False)

        # Finalize history
        self.write_history_file()
        self.generate_pdf()

    def add_history_item(self, action, doc_id, old_doc_title, old_version, old_datum, old_was_printed, new_doc_title,
                         new_version, new_datum, new_is_printed):
        item = HistoryItem()

        item.action = action
        item.doc_id = doc_id
        item.old_doc_title = old_doc_title
        item.old_version = old_version
        item.old_datum = old_datum
        item.old_was_printed = old_was_printed
        item.new_doc_title = new_doc_title
        item.new_version = new_version
        item.new_datum = new_datum
        item.new_is_printed = new_is_printed

        if action == ACTION_ADD:
            item.reason.append(REASON_ADD)
            item.changes.append("Version: " + new_version)
            item.changes.append("Datum: " + new_datum)
            if new_is_printed:
                item.checklist.extend(CHECKLIST_ADD_PRINTED)
        elif action == ACTION_REMOVE:
            item.reason.append(REASON_REMOVE)
            item.changes.append("Alte Version: " + old_version)
            item.changes.append("Altes Datum: " + old_datum)
            if old_was_printed:
                item.checklist.extend(CHECKLIST_REMOVE_PRINTED)
        elif action == ACTION_CHANGE:
            if old_doc_title != new_doc_title:
                item.reason.append(REASON_CHANGE_TITLE)
                item.changes.append("Titel: " + old_doc_title + " -> " + new_doc_title)
                if new_is_printed and old_was_printed:
                    item.checklist.extend(CHECKLIST_CHANGE_TITLE)
            if old_version != new_version or old_datum != new_datum:
                item.reason.append(REASON_CHANGE_VERSIONDATUM)
                if old_version != new_version:
                    item.changes.append("Version: " + old_version + " -> " + new_version)
                if old_datum != new_datum:
                    item.changes.append("Datum: " + old_datum + " -> " + new_datum)
                if new_is_printed and old_was_printed:
                    item.checklist.extend(CHECKLIST_CHANGE_VERSIONDATUM)
            if old_was_printed != new_is_printed:
                if new_is_printed:
                    # Was not printed and now it is
                    item.reason.append(REASON_PRINTED_NOW)
                    item.checklist.extend(CHECKLIST_ADD_PRINTED)
                else:
                    # Was printed and now not
                    item.reason.append(REASON_NOT_PRINTED_ANYMORE)
                    item.checklist.extend(CHECKLIST_REMOVE_PRINTED)

        self.historyItems.append(item)

    def read_last_entries(self):
        input_file = '/Historie_' + self.output_name + '.yaml'
        for input_folder in self.input_folders:
            if os.path.exists(input_folder + input_file):
                logger.debug("Find history file in " + input_folder + input_file)
                with open(input_folder + input_file, 'r') as file:
                    yaml_data = yaml.load(file)

                    if 'entries' in yaml_data:
                        for entry in yaml_data['entries']:
                            self.last_entries.append(HistoryEntry(entry))
                        logger.debug("Load old entries from " + input_folder + input_file)
                break
        return

    def add_current_state(self, entry, is_printed):
        stored_entry = {
            'docId': entry.docId,
            'docTitle': entry.docTitle,
            'datum': entry.datum,
            'version': entry.version,
            'wasPrinted': is_printed
        }

        self.current_state['entries'].append(stored_entry)
        return

    def write_history_file(self):
        output_file = self.folder_output + '/Historie_' + self.output_name + '.yaml'
        with open(output_file, 'w') as file:
            yaml.dump(self.current_state, file)
            logger.debug("Write new history file to " + output_file)

    def generate_pdf(self):
        history_file = self.folder_work + "/history.latex"
        pdf_file = self.folder_output + "/Änderungsverzeichnis_" + self.output_name + ".pdf"

        with open(history_file, 'w') as self.latexFile:
            self.latex_history_add_header()

            self.generate_history_data(self.entries)

            self.latex_history_add_footer()
        self.latexFile = None

        Utils.syscall("pdflatex -output-directory=" + self.folder_work + " " + history_file)
        Utils.syscall("pdflatex -output-directory=" + self.folder_work + " " + history_file)

        shutil.copy(history_file.replace(".latex", ".pdf"), pdf_file)

    def generate_history_data(self, entries):
        for item in self.historyItems:
            text = "\\textbf{" + item.doc_id + " "
            if len(item.new_doc_title) > 0:
                text += item.new_doc_title
            else:
                text += item.old_doc_title
            text += "} \\newline "

            for reason in item.reason:
                text += "- " + reason + " \\newline "

            for change in item.changes:
                text += change.replace("->", "$\\rightarrow$") + " \\newline "

            text += " & "

            for checklist in item.checklist:
                text += "$\\square$ " + checklist + " \\newline "

            text += " \\\\ \\midrule"

            self.latexFile.write(text + '\n')

    def latex_history_add_header(self):
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
        self.latexFile.write('\\usepackage{lastpage}\n')
        self.latexFile.write('\\usepackage{booktabs}\n')
        self.latexFile.write('\\usepackage{longtable}\n')
        self.latexFile.write('\\usepackage{amsmath}\n')
        self.latexFile.write('\\usepackage{amssymb}\n')
        self.latexFile.write('\\usepackage[left=1cm,top=2cm,right=1cm,bottom=2cm]{geometry}\n')
        self.latexFile.write('\\definecolor{ral3001}{cmyk}{0, 0.77, 0.77, 0.39}\n')
        self.latexFile.write('\\definecolor{backgroundGray}{cmyk}{0, 0, 0, 0.2}\n')
        self.latexFile.write('\\setkeys{Gin}{keepaspectratio}\n')
        self.latexFile.write('\\begin{document}\n')

        self.latexFile.write('\\thispagestyle{empty}\n')
        self.latexFile.write('\\begin{textblock*}{10cm}(0.65cm,0.9cm)\n')
        self.latexFile.write('\\colorbox{gray!30}{' + Utils.latex_escape(self.copyright) + '}\n')
        self.latexFile.write('\\end{textblock*}\n')

        self.latexFile.write('\\begin{textblock*}{19cm}(1cm,0.9cm)\n')
        self.latexFile.write('\\raggedleft\n')
        self.latexFile.write('\\colorbox{gray!30}{Vertraulich - Nur f\\"ur den Dienstgebrauch}\n')
        self.latexFile.write('\\end{textblock*}\n')

        self.latexFile.write('\\begin{textblock*}{19cm}(1cm,28.5cm)\n')
        self.latexFile.write('\\raggedleft\n')
        self.latexFile.write('\\colorbox{gray!30}{' + Utils.latex_escape(self.docTitle) + ' - Datum ' + self.datum + ' - Seite \\thepage/\pageref{LastPage}  - ' + self.docId + '}\n')
        self.latexFile.write('\\end{textblock*}\n')

        self.latexFile.write('\\begin{longtable}{p{10cm}p{5.5cm}}\n')
        self.latexFile.write('\\toprule\n')
        self.latexFile.write('\\endhead\n')
        self.latexFile.write('\\endfoot\n')
        self.latexFile.write('\\endlastfoot\n')

    def latex_history_add_footer(self):
        self.latexFile.write('\\end{longtable}\n')
        self.latexFile.write('\\end{document}\n')

