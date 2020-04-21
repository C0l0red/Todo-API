from functools import wraps
from flask import request, current_app
import jwt
from resources.user import User


def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "access-token" in request.headers:
            token = request.headers['access-token']

        if not token:
            return {"message": "Token is missing"}, 401
        
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return {"message": "Token is invalid"}, 401

        return f(current_user=current_user, *args, **kwargs)
    
    return decorated