from flask import Flask, request, jsonify, send_file
from pdf2image import convert_from_bytes
import os
from io import BytesIO
import zipfile

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if not request.data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        images = convert_from_bytes(request.data)
        
        image_data_list = []

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:

            for i, image in enumerate(images):
                img_io = BytesIO()
                image.save(img_io, 'PNG')
                img_io.seek(0)
                zip_file.writestr(f'page_{i + 1}.png', img_io.getvalue())

        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, attachment_filename='images.zip')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)