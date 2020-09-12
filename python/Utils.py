import subprocess
import logging
import re

# Set logging settings #################################################################################################

logger = logging.getLogger(__name__)

# Utils ################################################################################################################


def syscall(command):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    p_status = proc.wait()
    logger.debug(command)
    if proc.returncode != 0:
        if out and len(out) > 0:
            logger.info(str(out).replace('\\n', "\n"))
        if err and len(err) > 0:
            logger.error(str(err).replace('\\n', "\n"))
    else:
        if out and len(out) > 0:
            logger.debug(str(out).replace('\\n', "\n"))
        if err and len(err) > 0:
            logger.debug(str(err).replace('\\n', "\n"))

    return


def mkdir(directory):
    syscall("mkdir -p '" + directory + "'")


def rm(file):
    syscall("rm -f " + file)


def rm_recursive(folder):
    syscall("rm -r -f " + folder)


def latex_escape(text):
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: - len(item))))
    out = regex.sub(lambda match: conv[match.group()], text)
    # print('in "' + text + '" -> "' + out + '"')
    return out


def convert_yaml_bool(inputtext):
    input_lower = inputtext.lower()
    if input_lower == 'n' or input_lower == 'no' or input_lower == 'nein':
        return False
    if input_lower == 'y' or input_lower == 'yes' or input_lower == 'j' or input_lower == 'ja':
        return True

    logger.debug("Falscher boolean Wert: " + inputtext + " , nutze False")
    return False
