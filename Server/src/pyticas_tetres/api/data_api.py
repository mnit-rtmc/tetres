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
import common


def compress_data():
    outdir = common.DATA_PATH + "/tetres/clientdatafiles"

    os.makedirs(outdir, exist_ok=True)
    filename = 'data-' + str(time.strftime('%Y%m%d-%H%M%S')) + '.zip'

    newexclude = ['clientdatafiles', 'output']

    def do_zip_folder(path, relname, archive):
        paths = os.listdir(path)
        cleaned_paths = [p for p in paths if p not in newexclude]
        for p in cleaned_paths:
            p1 = os.path.join(path, p)
            p2 = os.path.join(relname, p)
            if os.path.isdir(p1):
                do_zip_folder(p1, p2, archive)
            else:
                archive.write(p1, p2)

    def create_zip(path, relname, archname):
        archive = zipfile.ZipFile(outdir + '/' + archname, "w", zipfile.ZIP_DEFLATED)
        if os.path.isdir(path):
            do_zip_folder(path, relname, archive)
        else:
            archive.write(path, relname)
        archive.close()

    create_zip(common.DATA_PATH + '/tetres', 'tetres', filename)

    return outdir, filename


def extract_data(filedir, filename):
    try:
        zip_ref = zipfile.ZipFile(filedir + '/' + filename, 'r')
        zip_ref.extractall(filedir)
        zip_ref.close()
        return True
    except:
        return False


def allowed_file(filename):
    return '..' not in filename and '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['zip', 'json', 'txt']


def register_api(app):
    @app.route(api_urls_client.DOWNLOAD_DATA, methods=['GET'])
    def tetres_client_download_data():
        """ Called when the client tries to download the data """
        try:
            outdir, filename = compress_data()
        except Exception as e:
            return prot.response_fail(message='Failed to compress data')

        return send_file(outdir + '/' + filename, as_attachment=True)

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
            filedir = common.DATA_PATH + "/tetres/clientdatafiles"

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

            filedir = common.DATA_PATH

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

        outdir = common.DATA_PATH

        os.remove(os.path.join(outdir, delete_path))
        return prot.response_success()
