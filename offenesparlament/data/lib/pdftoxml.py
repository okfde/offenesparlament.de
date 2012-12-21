import subprocess
import tempfile

def pdftoxml(data):
    fh, path = tempfile.mkstemp('.pdf')
    fo = open(path, 'wb')
    fo.write(data)
    fo.close()
    return pdftoxml_file(path)
    

def pdftoxml_file(file_path):
    process = subprocess.Popen(['pdftohtml', '-xml', '-noframes', '-stdout',
            file_path], shell=False, stdout=subprocess.PIPE)
    return process.stdout.read()
