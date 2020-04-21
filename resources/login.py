from flask import make_response, current_app, request
from .user import User
import jwt
import datetime
from werkzeug.security import check_password_hash
from api import api
from flask_restful import Resource
from api.main import token_required


#===============================================
#Resource


class Login(Resource):
    def get(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response("Enter a usename and password.", 401, {"WWW-Authenticate": "Basic-realm='Login Required'"})
        
        user = User.query.filter_by(username=auth.username).first()
        if not user:
            return make_response("User does not exist", 401, {"WWW-Authenticate": "Basic-realm='Login Required'"})
        
        hashed = check_password_hash(user.password, auth.password)
        if hashed:
            token = jwt.encode({"public_id": user.public_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
                                current_app.config["SECRET_KEY"])
            return {"message": f"User: {user.username}, you are now logged in",
                    "token": token.decode("UTF-8") }
        
        return make_response("Wrong Password", 401, {"WWW-Authenticate": "Basic-realm='Login Required'"})

