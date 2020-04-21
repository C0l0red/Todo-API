from .login import Login
from .todo import Todos
from .user import Users 

def initialize_routes(api):
    api.add_resource(Login, "/login")
    api.add_resource(Users, "/user", "/user/<public_id>")
    api.add_resource(Todos, "/todo", "/todo/<todo_id>")

