# -*- coding: UTF-8 -*-

import argparse
import logging
import os.path
import fnmatch
import yaml
import csv
import Utils
import coloredlogs

import InfoFile
import ProcessCopy
import ProcessLink
import ProcessPdf
import ProcessXslx
import ProcessDocx
import ProcessSla
import ProcessSlaSerie

import GeneratorPdfToc
import GeneratorHtmlToc
import GeneratorReiter
import GeneratorRedist
import GeneratorHistory

# TODO kontakte
# TODO Process SLA_Series
# TODO Generator Debian package

processors = {
    'copy': ProcessCopy.create_instance,
    'link': ProcessLink.create_instance,
    'pdf': ProcessPdf.create_instance,
    'xslx': ProcessXslx.create_instance,
    'docx': ProcessDocx.create_instance,
    'sla': ProcessSla.create_instance,
    'sla_serie': ProcessSlaSerie.create_instance,
}

generators = {
    'PdfToc': GeneratorPdfToc.create_instance,
    'HtmlToc': GeneratorHtmlToc.create_instance,
    'Reiter': GeneratorReiter.create_instance,
    'Redist': GeneratorRedist.create_instance,
    'Historie': GeneratorHistory.create_instance,
}

# Set logging settings #################################################################################################

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

# Parse command line arguments #########################################################################################

parser = argparse.ArgumentParser(description='Erstellung von Info-Ordnern')
parser.add_argument('--config', required=True, help='Configurationsdatei')
parser.add_argument('--cache', required=True, help='Cache Verzeichnis')
parser.add_argument('--work', required=True, help='Arbeitsverzeichnis')
parser.add_argument('--output', required=True, help='Ausgabeverzeichnis')
parser.add_argument('--cleancache', action="store_true", help='Bereinigt den cache')
parser.add_argument('ordner', metavar='O', nargs='+', help='Verzeichnis zum Einlesen')
args = parser.parse_args()

configFile = os.path.abspath(args.config)
folderCache = os.path.abspath(args.cache)
folderWork = os.path.abspath(args.work)
folderOutput = os.path.abspath(args.output)

logger.info("Cache Verzeichnis: " + folderCache)
logger.info("Arbeitsverzeichnis: " + folderWork)

# Variables ############################################################################################################

availableSetsAndOutputs = []

# Read configuration file ##############################################################################################

with open(configFile) as config_yaml_file:
    configData = yaml.load(config_yaml_file)

# Search all files #####################################################################################################

logger.info("Suche Dateien zum Verarbeiten")

files = []
for rawFolder in args.ordner:
    logger.debug("Durchsuche: " + rawFolder)
    for root, dirnames, filenames in os.walk(rawFolder):
        for filename in fnmatch.filter(filenames, '*.yaml'):
            if os.path.join(root, filename) == configFile:
                # Ignore main configuration file
                continue

            logger.debug("Füge hinzu: " + filename)
            files.append(os.path.join(root, filename))

# Read files ###########################################################################################################

logger.info("Lese Dateien ein")

infoFiles = []
for rawFile in files:
    infoFile = InfoFile.InfoFile(rawFile, processors)

    if infoFile.valid:
        infoFiles.append(infoFile)

        for curr_set in infoFile.sets:
            if curr_set.name not in availableSetsAndOutputs:
                availableSetsAndOutputs.append(curr_set.name)

# Sort info files ######################################################################################################

logger.info("Sortiere Dateien")

sortedInfoFiles = sorted(infoFiles, key=lambda sort_entry: (sort_entry.folder, sort_entry.docId))

# Create caches ########################################################################################################

if args.cleancache:
    logger.info("Bereinige cache")
    Utils.mkdir(folderCache)
    Utils.rm(folderCache + "/*")

logger.info("Bereinige work")
Utils.mkdir(folderWork)
Utils.rm(folderWork + "/*")

logger.info("Erstelle Cache")

for i in sortedInfoFiles:
    processor = processors[i.type](i)
    processor.create_cache(folderCache, folderWork)

    i.set_cache_files(processor.cache_files())

# Generate outputs #####################################################################################################

logger.info("Bereinige Ausgabeverzeichnis")
Utils.mkdir(folderOutput)
Utils.rm_recursive(folderOutput)
Utils.mkdir(folderOutput)

for output in configData['outputs']:
    name = output['name']
    availableSetsAndOutputs.append('OUTPUT_' + name)

    sets = output['sets']
    included_generators = output['generators']

    customOutputPath = folderOutput + "/" + name
    Utils.mkdir(customOutputPath)

    logger.info("Erstelle Ausgabe für " + name)

    filteredEntries = [d for d in sortedInfoFiles if d.is_for_sets(sets)]

    logger.info("Kopiere Dateien aus Cache")
    for entry in filteredEntries:
        entry.copy_cache(customOutputPath)

        entry.add_used_output(name, entry.is_printed_in_sets(sets))

    if included_generators:
        logger.info("Starte Generatoren")
        for generator in included_generators:
            gen_name = generator['generator']
            gen_params = []
            if 'parameters' in generator:
                gen_params = generator['parameters']

            gen = generators[gen_name](name, gen_params, filteredEntries, sets, folderWork, customOutputPath, args.ordner)
            gen.generate()

# Write overview CSV ###################################################################################################

with open(folderOutput + '/output.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=';',
                           quotechar='|', quoting=csv.QUOTE_MINIMAL)

    csvwriter.writerow(['Datei'] + availableSetsAndOutputs)
    for entry in sortedInfoFiles:
        entryData = [entry.docId + '_' + entry.docTitle] + [''] * len(availableSetsAndOutputs)

        for curr_set in entry.sets:
            index = availableSetsAndOutputs.index(curr_set.name) + 1
            if curr_set.printed:
                entryData[index] = 'X'
            else:
                entryData[index] = 'nG'

        for gen in entry.usedOutputs:
            index = availableSetsAndOutputs.index('OUTPUT_' + gen.name) + 1
            if gen.printed:
                entryData[index] = 'X'
            else:
                entryData[index] = 'nG'

        csvwriter.writerow(entryData)

# Finish ###############################################################################################################

logger.info("Verarbeitung abgeschlossen")
