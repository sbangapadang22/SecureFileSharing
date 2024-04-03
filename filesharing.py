import os
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import uuid
import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_FILE_SIZE'] = 16 * 1024 * 1024  # 16MB

db = SQLAlchemy(app)

class File(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    encrypted_data = db.Column(db.LargeBinary, nullable=False)
    encryption_key = db.Column(db.LargeBinary, nullable=False)
    views = db.Column(db.Integer, nullable=False)
    max_views = db.Column(db.Integer, nullable=False)
    expires = db.Column(db.DateTime)

def generate_encryption_key():
    return AESGCM.generate_key(bit_length=256)

def encrypt_file(file_data, encryption_key):
    aesgcm = AESGCM(encryption_key)
    nonce = os.urandom(12)
    encrypted_data = aesgcm.encrypt(nonce, file_data, None)
    return nonce + encrypted_data

def decrypt_file(encrypted_data, encryption_key):
    aesgcm = AESGCM(encryption_key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    views = int(request.form.get('views', 1))
    expiration = request.form.get('expiration')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file.content_length > app.config['MAX_FILE_SIZE']:
        return jsonify({'error': 'File size exceeds the limit'}), 400

    filename = secure_filename(file.filename)
    file_data = file.read()

    encryption_key = generate_encryption_key()
    encrypted_data = encrypt_file(file_data, encryption_key)

    file_id = str(uuid.uuid4())
    expires = datetime.datetime.strptime(expiration, '%Y-%m-%d') if expiration else None

    new_file = File(
        id=file_id,
        filename=filename,
        encrypted_data=encrypted_data,
        encryption_key=encryption_key,
        views=views,
        max_views=views,
        expires=expires
    )
    db.session.add(new_file)
    db.session.commit()

    share_url = request.host_url + 'download/' + file_id

    return jsonify({'shareUrl': share_url}), 200

@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    file = File.query.get(file_id)

    if not file:
        return jsonify({'error': 'File not found'}), 404

    if file.views <= 0:
        return jsonify({'error': 'File has expired'}), 410

    if file.expires and datetime.datetime.now() > file.expires:
        return jsonify({'error': 'File has expired'}), 410

    decrypted_data = decrypt_file(file.encrypted_data, file.encryption_key)

    file.views -= 1
    if file.views == 0:
        db.session.delete(file)
    db.session.commit()

    return send_file(decrypted_data, attachment_filename=file.filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    db.create_all()
    app.run()