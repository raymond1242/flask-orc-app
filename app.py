import os
import io
import jwt
from uuid import uuid4
from dotenv import load_dotenv
from flask import Flask, jsonify, request, make_response, Response
from flask_sqlalchemy import SQLAlchemy
from PIL import Image as PILImage
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
from pytesseract import image_to_string

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

IS_PRODUCTION = os.getenv('ENVIRONMENT') == 'production'

if IS_PRODUCTION:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    image_data = db.Column(db.LargeBinary, nullable=False)
    mime_type = db.Column(db.String)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing'}), 401
  
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(email=data['email']).first()
        except Exception as e:
            return jsonify({'message' : 'Invalid token', 'error': f'{e}'}), 401
        return  f(current_user, *args, **kwargs)
  
    return decorated


@app.route('/users', methods =['GET'])
@token_required
def get_all_users(current_user):
    print(current_user)
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            'id': user.id,
            'name' : user.name,
            'email' : user.email
        })
  
    return jsonify({'users': output})


@app.route('/login', methods =['POST'])
def login():
    auth = request.form
  
    if not auth or not auth.get('email') or not auth.get('password'):
        return make_response('Missing parameters', 400)
  
    user = User.query.filter_by(email=auth.get('email')).first()
  
    if not user:
        return make_response('User does not exist', 401)

    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({
            'email': user.email,
        }, app.config['SECRET_KEY'], algorithm="HS256")
  
        return make_response(jsonify({'token' : token}), 201)

    return make_response('Incorrect credentials', 401)


@app.route('/signup', methods =['POST'])
def signup():
    data = request.form

    if not data.get('name') or not data.get('email') or not data.get('password'):
        return make_response('Missing parameters', 400)

    user = User.query.filter_by(email=data.get('email', None)).first()
    if not user:
        user = User(
            name = data.get('name'),
            email = data.get('email'),
            password = generate_password_hash(data.get('password'))
        )
        db.session.add(user)
        db.session.commit()
  
        return make_response('Successfully registered.', 201)
    else:
        return make_response('User already exists. Please Log in.', 202)


@app.route('/image', methods =['POST'])
@token_required
def upload_image(current_user):
    image = request.files['image']
    if not image:
        return make_response('Missing image', 400)
    try:
        image_uuid = str(uuid4())
        image = Image(
            uuid = image_uuid,
            user_id = current_user.id,
            image_data = image.read(),
            mime_type = image.mimetype
        )
        db.session.add(image)
        db.session.commit()
        return make_response(jsonify({'image_uuid': image_uuid}), 201)
    except Exception as e:
        return make_response(jsonify({'error': f'{e}'}), 500)


@app.route('/image/<image_uuid>', methods =['GET'])
@token_required
def get_image(current_user, image_uuid):
    image = Image.query.filter_by(uuid=image_uuid).first()
    if not image:
        return 'Image not found', 404
    return Response(image.image_data, mimetype=image.mime_type)


@app.route('/extract_text/<image_uuid>', methods =['GET'])
@token_required
def extract_text(current_user, image_uuid):
    image = Image.query.filter_by(uuid=image_uuid).first()
    if not image:
        return make_response('Image not found', 404)
    
    byte_image = PILImage.open(io.BytesIO(image.image_data))
    text = image_to_string(byte_image)
    return make_response(jsonify({'text': text}), 200)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
