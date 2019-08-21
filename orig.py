from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime
from functools import wraps
import time
from datetime import datetime, timedelta

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'akshay'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')

db = SQLAlchemy(app)

class User(db.Model):
    u_id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(50), unique=True)
    passwd = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean)

class Content(db.Model):
    c_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.String(1024))
    summary = db.Column(db.String(256))
    file_link = db.Column(db.String(100))
    categories = db.Column(db.String(1024))
    user_id = db.Column(db.Integer)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token missing!'}), 401

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(u_id=data['u_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# Code for login and registration
@app.route('/registration', methods=['POST'])
def registration():
    data = request.get_json()
    if data['uname'] == '' or data['passwd'] == '':
        return jsonify({'message' : 'please provide all values'})

    user = User.query.filter_by(uname=data['uname']).first()
    if user:
        return jsonify({'message' : 'User already exists!'})
    else:
        hashed_pwd = generate_password_hash(data['passwd'], method='sha256')
        new_user = User(uname = data['uname'], passwd = hashed_pwd, is_admin=data['is_admin'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'msg' : 'new user created'})

@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message' : 'Please provide all details'})

    user = User.query.filter_by(uname=auth.username).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    if check_password_hash(user.passwd, auth.password):
        token = jwt.encode({'u_id' : user.u_id, 'is_admin' : user.is_admin, 'exp' : datetime.utcnow() + timedelta(minutes=60)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})

    return jsonify({'message' : 'Something went wrong!'})

# code to get all content for a particular user
@app.route('/api/contents', methods=['GET'])
@token_required
def get_all_content(current_user):
    page = 1
    total_pages = 0
    current_page = 0
    next_page_url = 0
    prev_page_url = 0
    if request.args.get('page') is not None:
        page = int(request.args.get('page'))


    if current_user.is_admin:
        contents = Content.query.paginate(per_page=2, page=page)
        total_pages = contents.pages
        current_page = contents.page
        if contents.has_next:
            next_page_url = '127.0.0.1:5000/contents?page='+str(contents.next_num)
        else: 
            next_page_url = 'last page'
        if contents.has_prev:
            prev_page_url = '127.0.0.1:5000/contents?page='+str(contents.prev_num)
        else:
            prev_page_url = 'first page'
        # contents = Content.query.all()
    else:
        contents = Content.query.filter_by(user_id=current_user.u_id).paginate(per_page=2, page=page)
        total_pages = contents.pages
        current_page = contents.page
        if contents.has_next:
            next_page_url = '127.0.0.1:5000/contents?page='+str(contents.next_num)
        if contents.has_prev:
            prev_page_url = '127.0.0.1:5000/contents?page='+str(contents.prev_num)

    output = []
    for content in contents.items:        
        content_data = {}
        content_data['c_id'] = content.c_id
        content_data['title'] = content.title
        content_data['body'] = content.body
        content_data['summary'] = content.summary
        content_data['file_link'] = content.file_link
        content_data['user_id'] = content.user_id
        content_data['catogories'] = content.categories
        output.append(content_data)
    page_data = {}
    page_data['total_pages'] = total_pages
    page_data['current_page'] = current_page
    page_data['next_page_url'] = next_page_url
    page_data['prev_page_url'] = prev_page_url


    return jsonify({'contents' : output, 'paginate': page_data})

# code to get single content for a particular user
@app.route('/api/content/<c_id>', methods=['GET'])
@token_required
def get_one_content(current_user, c_id):
    content = Content.query.filter_by(c_id=c_id, user_id=current_user.u_id).first()

    if not content:
        return jsonify({'message' : 'No content found!'})
    if not current_user.is_admin:
        content_data = {}
        content_data['c_id'] = content.c_id
        content_data['title'] = content.title
        content_data['body'] = content.body
        content_data['summary'] = content.summary
        content_data['file_link'] = content.file_link
        content_data['user_id'] = content.user_id
        content_data['catogories'] = content.categories
        return jsonify(content_data)
    return jsonify({'message': 'something wnt wrong'})

# need to give form data for file upload
@app.route('/api/content', methods=['POST'])
@token_required
def create_content(current_user):
    data = request.form.to_dict()
    file = request.files['document']
    if not current_user.is_admin:
        

        if 'document' in request.files:
            
            if not file.content_type == 'application/pdf':
                return jsonify({'msg': 'only pdf files are allowed'})

        if data['title'] == '' or data['body'] =='' or data['summary'] == '' or data['categories'] == '':
            return jsonify({'message' : 'please fill all details.'})

        file.save('uploads/'+str(current_user.u_id)+'-'+str(int(time.time()))+'.pdf')
        new_content = Content(title=data['title'], body=data['body'], summary=data['summary'], file_link=str(current_user.u_id)+'-'+str(int(time.time()))+'.pdf', categories=data['categories'], user_id=current_user.u_id)
        db.session.add(new_content)
        db.session.commit()

        return jsonify({'message' : "content created!"})
    else:
        return jsonify({'msg': 'not permitted to create content'})

# need to give form data for file upload
@app.route('/api/content/<c_id>', methods=['PUT'])
@token_required
def update_content(current_user, c_id):
    # data = request.get_json()
    data = request.form.to_dict()
    file = request.files['document']
    if not current_user.is_admin:
        content = Content.query.filter_by(c_id=c_id, user_id=current_user.u_id).first()
    else:
        return jsonify({'msg': 'unable to update'})

    file = request.files['document']
    file_link = content.file_link
    if 'document' in request.files:    
        if not file.content_type == 'application/pdf':
            return jsonify({'msg': 'only pdf files are allowed'})

    if not content:
        return jsonify({'message' : 'No content found!'})

    if 'title' in data and data['title'] != '' and data['title'] != content.title:
        content.title = data['title']
    if 'body' in data and data['body'] != '' and data['body'] != content.body:
        content.body = data['body']
    if 'summary' in data and data['summary'] != '' and data['summary'] != content.summary:
        content.summary = data['summary']
    print(file_link)
    if file:
        os.remove('uploads/'+str(content.file_link))
        file.save('uploads/'+str(current_user.u_id)+'-'+str(int(time.time()))+'.pdf')
        content.file_link = str(current_user.u_id)+'-'+str(int(time.time()))+'.pdf'
    if 'categories' in data and data['categories'] != '':
        content.categories = ', '.join(list(set(content.categories.split(', ')+data['categories'].split(', '))))

    db.session.commit()

    return jsonify({'message' : 'Content updated'})

@app.route('/api/content/<content_id>', methods=['DELETE'])
@token_required
def delete_content(current_user, content_id):
    if not current_user.is_admin:
        content = Content.query.filter_by(c_id=content_id, user_id=current_user.u_id).first()
    else:
        return jsonify({'msg': 'not accessible'})

    if not content:
        return jsonify({'message' : 'No content found!'})
    
    db.session.delete(content)
    os.remove('uploads/'+str(content.file_link))
    db.session.commit()

    return jsonify({'message' : 'content item deleted!'})

if __name__ == '__main__':
    app.run(debug=True)
