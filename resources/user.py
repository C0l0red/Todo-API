from api import api, db
from flask import current_app, request
from flask_restful import Resource
from werkzeug.security import check_password_hash, generate_password_hash

#===============================================
#Model
"""
This is the single model that represents a user: 
an id for the database, 
a public id to be used with on the API, 
admin to exercise administrative privledges, 
and a password for securing User accounts
"""

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, index=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    admin = db.Column(db.Boolean, default=False)


#===============================================
#Resource
"""
This is the User Resource, containing all the available HTTP methods for User.
POST request lets you create a new User, you submit a JSON containing a username and password using the POST method
GET request lets you:
        1. WITHOUT ANY ARGUMENTS. View all Users if you're an admin(if your admin attribute is True)
        2. WITH AN ARGUMENT(Your own public ID). View your User account
PUT request takes an argument (A public ID) lets you promote any user to an admin as long as you're an admin yourself.
DELETE request takes an argument (A Public ID) lets you delete a user, as long as you're an admin yourself
"""
from api.main import token_required

class Users(Resource):
    def post(self):
        data = request.get_json()

        if all (x in data.keys() for x in ['username','password']):
            if User.query.filter_by(username=data['username']).first():
                return {"message": "User already exists"} 

            hashed = generate_password_hash(data['password'], method='sha256')
            new_user = User(username=data['username'], password=hashed, admin=False, public_id=str(uuid.uuid4()))
            db.session.add(new_user)
            db.session.commit()
            return {'message': f"User: {new_user.username} has been created"}, 201

        return {"message": "Please, pass in a username and password in JSON format to create a user."}
    
    @token_required
    def get(self, current_user, public_id=None):
        if public_id:
            user = User.query.filter_by(public_id=public_id).first()
            if user is None:
                return {"message": "User not found"}, 404
            data = {"username": user.username,
                    "password": user.password,
                    "admin": user.admin,
                    "public_id": user.public_id}
            return data
        users = User.query.all()
        output = []
        for user in users:
            data = {"username": user.username,
                    "password": user.password,
                    "admin": user.admin,
                    "public_id": user.public_id}
            output.append(data)
        if not output:
            return {"message": "No users yet"}
        return {'users': output}

    @token_required
    def put(self,current_user, public_id):
        user = User.query.filter_by(public_id=public_id).first()
        if user is None:
            return {"message": "User not found"}, 404
        user.admin = True
        return {"message": f"{user.username} has been promoted to admin."}

    @token_required
    def delete(self, current_user, public_id):
        user = User.query.filter_by(public_id=public_id).first()
        if user is None:
            return {"message": "User not found"}, 404
        
        name = user.username
        db.session.delete(user)
        db.session.commit()

        return {"message": f"User: {name} has been deleted."}