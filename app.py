from flask import Flask, request, jsonify, send_file, url_for, send_from_directory
from pdf2image import convert_from_bytes
from io import BytesIO
import zipfile
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = '/home/vrclassroom/uploads'
SERVER_URL = 'vrclassroom.pythonanywhere.com'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/convert-pdf-png', methods=['POST'])
def convert_pdf_to_png():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected for uploading'}), 400

        file_bytes = file.read()

        images = convert_from_bytes(file_bytes, dpi=200, fmt='png')

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:

            for i, image in enumerate(images):
                img_io = BytesIO()
                image.save(img_io, 'PNG')
                img_io.seek(0)
                zip_file.writestr(f'page_{i + 1}.png', img_io.getvalue())

        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True,
                         download_name='images.zip')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_url = url_for('uploaded_file', filename=filename, _external=True)
        return jsonify({'url': file_url})

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
   
    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    images = convert_from_bytes(file_bytes, dpi=200, fmt='png')

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for i, image in enumerate(images):
            img_io = BytesIO()
            image.save(img_io, 'PNG')
            img_io.seek(0)
            zip_file.writestr(f'page_{i + 1}.png', img_io.getvalue())

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True,
                     download_name='images.zip')

