from flask import Flask, render_template, send_file, request, Response, flash
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS, IMAGES
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
import tika
from tika import parser
from flask import send_file

app = Flask(__name__)

docs = UploadSet('datafiles', DOCUMENTS)
app.config['UPLOADED_DATAFILES_DEST'] = 'static/uploads'
configure_uploads(app, docs)


@app.route('/')
def index():
    return render_template('index.html')


def only_numerics(seq):
    seq_type = type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))


@app.route("/upload", methods=['GET', 'POST'])
def upload():

    # user_file is the name value in input element
    filename = ""
    if request.method == 'POST' and 'user_file' in request.files:
        filename = docs.save(request.files['user_file'])

        raw = parser.from_file("static/uploads/" + filename)
        text = raw['content']
        regex = '\d{10}'
        matchSAP = re.findall(regex, text, flags=re.DOTALL)
        filteredSAP = []
        for x in matchSAP:
            if x.startswith("1"):
                filteredSAP.append(x)

        print(filteredSAP)

        regex2 = '\d+\s+Sztuka'
        amount = re.findall(regex2, text)
        print(amount)

        amount2 = []
        for x in amount:
            amount2.append(only_numerics(x))
        print(amount2)

        zipper = zip(filteredSAP, amount2)
        dictionary = dict(zipper)
        print(dictionary)

        with open('output.csv', 'w') as f:
            f.write("Numer SAP, ilosc sztuk\n")
            for key in dictionary.keys():
                f.write("%s,%s\n" % (key, dictionary[key]))

    return render_template('upload.html')

@app.route("/upload")
def alert():
    if upload:
        flash('ready to download')
    return render_template('upload.html')

@app.route("/download")
def download_csv():
    path = "output.csv"
    return send_file(path, as_attachment=True)
