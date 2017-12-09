from __future__ import print_function
from flask import Flask, request, redirect, render_template, send_from_directory
from uuid import uuid4
import os
import json
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import threading
from time import sleep
from werkzeug.utils import secure_filename
from processing_unit import process_input

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/WebAppSunScene'
URL_ROOT = None


def files_folder(identifier):
    folder = os.path.join(UPLOAD_FOLDER, identifier)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def json_file(identifier):
    return files_folder(identifier)+'.json'


def load_data(identifier):
    try:
        with open(json_file(identifier), 'r') as fp:
            saved_data = json.load(fp)
    except IOError:
        saved_data = {}
    return saved_data


def save_data(data, identifier):
    saved_data = load_data(identifier)
    saved_data.update(data)
    with open(json_file(identifier), 'w') as fp:
        json.dump(saved_data, fp)


def save_file(the_file, identifier, filename):
    the_file.save(os.path.join(files_folder(identifier), filename))


def send_mail(toaddr, identifier):
    fromaddr = "pysunscene@gmail.com"
    frompasswd = "uibdmidfis"

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

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, frompasswd)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


def process_request(identifier):
    # Call the processing unit
    sleep(1)
    dirname = files_folder(identifier)
    datafile = json_file(identifier)
    process_input(datafile, dirname)
    # Send mail with link
    data = load_data(identifier)
    send_mail(toaddr=data['email'], identifier=identifier)


@app.route('/')
def hello():
    global URL_ROOT
    if URL_ROOT is None:
        URL_ROOT = request.url_root
    return redirect('/node/start')


@app.route('/node/<name>/<identifier>', methods=['GET', 'POST'])
@app.route('/node/<name>', methods=['GET', 'POST'])
def node(name, identifier=None):
    if request.method == 'GET':
        return render_template(name + ".html", identifier=identifier)
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
                save_file(the_file, identifier, filename)
                data[file_id] = filename
        save_data(data, identifier)
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
    return render_template("end.html")


@app.route('/results/<identifier>', methods=['GET'])
@app.route('/results/')
def send_file(identifier=None):
    if identifier is None:
        return "No process job specified"
    return send_from_directory(UPLOAD_FOLDER, identifier + '.output')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, threaded=True)
