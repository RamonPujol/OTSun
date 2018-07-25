from __future__ import print_function
from flask import Flask, request, redirect, render_template, send_from_directory, current_app
import flask
from uuid import uuid4
import os
import shutil
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
from werkzeug.utils import secure_filename
from processing_unit import process_experiment, run_processor
from materials import create_material
import logging
import webappsunscene.default_settings

app = Flask(__name__, static_url_path='/static_file')
app.config.from_object(webappsunscene.default_settings)
app.config.from_envvar("OTSUN_CONFIG_FILE", silent = True)

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
if not os.path.exists(UPLOAD_FOLDER):
    app.logger.info('creating upload folder')
    os.makedirs(UPLOAD_FOLDER)
else:
    if not os.access(UPLOAD_FOLDER, os.W_OK):
        UPLOAD_FOLDER += str(uuid4())
        os.makedirs(UPLOAD_FOLDER)
URL_ROOT = None

MAIL_SENDER = app.config['MAIL_SENDER']
MAIL_SERVER = app.config['MAIL_SERVER']
MAIL_PASSWD = app.config['MAIL_PASSWD']
MAIL_PORT = app.config['MAIL_PORT']


# formatter = logging.Formatter(
#     "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
# handler = RotatingFileHandler(LOG_FILE, maxBytes=1000000, backupCount=5)
# handler.setLevel(logging.INFO)
# handler.setFormatter(formatter)
# logging.addHandler(handler)


def root_folder(identifier):
    folder = os.path.join(UPLOAD_FOLDER, identifier)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def files_folder(identifier):
    folder = os.path.join(root_folder(identifier), 'files')
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def json_filename(identifier):
    return os.path.join(root_folder(identifier), 'data.json')


def status_file(identifier):
    return os.path.join(root_folder(identifier), 'status.json')


def load_json(filename):
    try:
        with open(filename, 'r') as fp:
            saved_data = json.load(fp)
    except IOError:
        saved_data = {}
    return saved_data


def load_data(identifier):
    return load_json(json_filename(identifier))


def save_data(data, identifier):
    saved_data = load_data(identifier)
    saved_data.update(data)
    with open(json_filename(identifier), 'w') as fp:
        json.dump(saved_data, fp)


def save_file(the_file, identifier, filename):
    the_file.save(os.path.join(files_folder(identifier), filename))


def send_mail(toaddr, identifier):
    app.logger.info("Sending mail for id %s", identifier)
    fromaddr = MAIL_SENDER
    frompasswd = MAIL_PASSWD

    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Results of computation of PySunScene"

    body = """\
    <html>
    Get your results at:
    <a href="%s">link</a>
    </html>
    """ % (URL_ROOT + 'results/' + identifier)

    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
    server.starttls()
    server.login(fromaddr, frompasswd)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


def process_request(identifier, should_send_mail = True):
    app.logger.info("Processing request for id %s", identifier)
    # Call the processing unit
    dirname = root_folder(identifier)
    datafile = json_filename(identifier)
    process_experiment(datafile, dirname)
    # Send mail with link
    data = load_data(identifier)
    if should_send_mail:
        send_mail(toaddr=data['email'], identifier=identifier)


def process_processor(identifier):
    app.logger.info("Processing processor for id %s", identifier)
    # Call the processing unit
    dirname = root_folder(identifier)
    datafile = json_filename(identifier)
    return run_processor(datafile, dirname)

@app.before_request
def pre_prequest_logging():
    app.logger.info("Got %s request of url %s from ip %s",
                    request.method,
                    request.url,
                    request.remote_addr)

@app.route('/')
def hello():
    global URL_ROOT
    if URL_ROOT is None:
        URL_ROOT = request.url_root
    return redirect('node/start')


@app.route('/node/<name>/<identifier>', methods=['GET', 'POST'])
@app.route('/node/<name>', methods=['GET', 'POST'])
def node(name, identifier=None):
    if request.method == 'GET':
        if identifier:
            data = load_data(identifier)
        else:
            data = {}
        return render_template(name + ".html", identifier=identifier, data=data)
    if request.method == 'POST':
        data = request.form.to_dict()
        if identifier is None:
            identifier = str(uuid4())
        file_ids = request.files
        for file_id in file_ids:
            the_file = request.files[file_id]
            if the_file and the_file.filename != "":
                filename = the_file.filename
                filename = secure_filename(filename)
                app.logger.debug("filename is %s", filename)
                save_file(the_file, identifier, filename)
                data[file_id] = filename
        save_data(data, identifier)
        if 'processor' in data:
            new_data = process_processor(identifier)
            save_data(new_data, identifier)
        if 'next_step' in data:
            return redirect('node/' + data['next_step'] + '/' + identifier)
        else:
            return redirect('end/' + identifier)


@app.route('/end/<identifier>')
def end_process(identifier):
    global URL_ROOT
    if URL_ROOT is None:
        URL_ROOT = request.url_root
    compute_thread = threading.Thread(target=process_request, args=(identifier,))
    compute_thread.start()
    return render_template("end.html", identifier=identifier)


@app.route('/status/<identifier>')
def status(identifier):
    data_status = load_json(status_file(identifier))
    if not data_status:
        return render_template("error.html", identifier=identifier)
    return render_template("status.html", identifier=identifier, data_status=data_status)


@app.route('/results/<identifier>', methods=['GET'])
@app.route('/results/')
def send_file(identifier=None):
    if identifier is None:
        return "No process job specified"
    return send_from_directory(root_folder(identifier), 'output.zip')


@app.route('/static_file/<path:filename>')
def send_static_file(filename):
    return current_app.send_static_file(filename)
    #   send_from_directory(app.static_folder, filename)

@app.route('/material', methods=['GET','POST'])
def material():
    if request.method == 'GET':
        return render_template('materials.html')
    if request.method == 'POST':
        data = request.form.to_dict()
        app.logger.info("creating material with data: %s", data)
        files = request.files
        filename = create_material(data, files)
        return flask.send_file(filename,as_attachment=True)


def run_offline(identifier):
    root1 = root_folder(identifier)
    n = 1
    while os.path.exists(root1+'-'+str(n)):
        n += 1
    identifier2 = identifier+'-'+str(n)
    root2 = root1+'-'+str(n)
    os.makedirs(root2)
    shutil.copy(os.path.join(root1,'data.json'),os.path.join(root2,'data.json'))
    shutil.copytree(os.path.join(root1,'files'),os.path.join(root2,'files'))
    global URL_ROOT
    process_request(identifier2, should_send_mail=False)
    app.logger.info('Finished %s', identifier2)

if __name__ == '__main__':
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    app.logger.debug("Starting")
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=5002, threaded=True, debug=True)
