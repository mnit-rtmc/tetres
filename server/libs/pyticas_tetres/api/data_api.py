import os
import tarfile
import zipfile
import time

from flask import request, send_file, flash

from pyticas.tool import json
from pyticas_server import protocol as prot
from pyticas_tetres import api_urls_client
from pyticas_tetres.est import workers
from pyticas_tetres.est.helper import util

def compress_data():
    outdir = 'server/datafiles'
    os.makedirs(outdir, exist_ok=True)
    filename = 'data-' + str(time.strftime('%Y%m%d-%H%M%S')) + '.zip'
    exclude = ['data/cache','data/map','data/db','data/metro','data/log',
            'data/tetres/results','data/tetres/output','data/tetres/task_log']
    z = zipfile.ZipFile(outdir + '/' + filename, 'w')

    # root: starts with server/data, represents every directory
    # directories: list of directories in root
    for root, directories, files in os.walk('server/data'):
        prefix = root[7:].split('/')
        if len(prefix) > 1:
            prefix = prefix[0] + '/' + prefix[1]
        else:
            prefix = prefix[0]
        if prefix not in exclude:
            for fname in files:
                filepath = os.path.join(root,fname)
                z.write(filepath)

    z.close()
    return outdir, filename
    
def extract_data(filedir,filename):
    try: 
        zip_ref = zipfile.ZipFile(filedir + '/' + filename, 'r')
        zip_ref.extractall(filedir)
        zip_ref.close()
        return True
    except:
        return False

def allowed_file(filename):
    return '..' not in filename and '.' in filename and \
            filename.rsplit('.',1)[1].lower() in ['zip','json','txt']

def register_api(app):
    @app.route(api_urls_client.DOWNLOAD_DATA, methods=['GET'])
    def tetres_client_download_data():
        """ Called when the client tries to download the data """
        try:
            outdir, filename = compress_data()
        except Exception as e:
            return prot.response_fail(message='Failed to compress data')
        return send_file(os.getcwd() + '/' + outdir + '/' + filename, as_attachment=True)

    @app.route(api_urls_client.UPLOAD_DATA, methods=['POST'])
    def tetres_client_upload_data():
        """ Called when the client tries to upload the data """
        if 'file' not in request.files:
            return prot.response_fail('No file part')
        file = request.files['file']
        if file.filename == '':
            return prot.response_fail('No selected file')
        if file and allowed_file(file.filename):
            filename = 'data.zip'
            filedir = os.getcwd() + '/server'
            file.save(os.path.join(filedir, filename))
            success = extract_data(filedir, filename)
            if success:
                return prot.response_success()
            else:
                return prot.response_fail('Failed to extract data')
        return prot.response_fail('Failed to save/extract data')

    @app.route(api_urls_client.UPLOAD_FILE, methods=['POST'])
    def tetres_client_upload_file():
        """ Called when the client tries to upload a single file """
        if 'file' not in request.files:
            return prot.response_fail('No file part')
        file = request.files['file']
        if file.filename == '':
            return prot.response_fail('No selected file')
        if file and allowed_file(file.filename):
            filedir = os.getcwd() + '/server/data'
            path = os.path.join(filedir, file.filename)
            success = file.save(path)
            if success:
                return prot.response_success()
            else:
                return prot.response_fail('Failed to save file')
        return prot.response_fail('Failed to save file')

    @app.route(api_urls_client.DELETE_DATA, methods=['GET'])
    def tetres_client_delete_data():
        """ Called when the client tries to delete data """
        delete_path = request.args.get("path")
        outdir = "server/data"
        os.remove(os.path.join(outdir, delete_path))
        return prot.response_success()
