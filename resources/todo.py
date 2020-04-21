from api import api, db
from flask import current_app, request
from flask_restful import Resource
from api.main import token_required


#===============================================
#Model


class Todo(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False, unique=True)
    complete = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer)


#===============================================
#Resources



class Todos(Resource):
    @token_required
    def post(self, current_user):
        data = request.get_json()

        if 'text' in data.keys():
            todo = Todo(text=data['text'], user_id=current_user.id) 
            if todo in Todo.query.all():
                return {"message": "Todo item already exists. Please, try a new todo"} 
            
            db.session.add(todo)
            db.session.commit()
            return {"message": f"Todo: {todo.text} created and is yet to be completed"}, 201

        return {"message": "Please enter a 'text' and 'user_id' in JSON format"}

    @token_required
    def get(self, current_user, todo_id=None):
        if todo_id:
            todos = Todo.query.filter_by(id=todo_id, user_id=current_user.public_id).all()
            if not todos:
                return {"message": "Todo item not found."}
        else:
            todos = Todo.query.filter_by(user_id=current_user.public_id).all()
            
        output = []
        for todo in todos:
            output.append({'text': todo.text,
                            "complete": todo.complete})
        key = "todo" if len(output) == 1 else "todos"
        return { key: output}

    @token_required
    def put(self, current_user, todo_id):
        todo = Todo.query.filter_by(id=todo_id, user_id=current_user.public_id).first()
        if not todo:
            return {"message": "Todo item not found."}

        todo.complete = True
        db.commit()
        return {"message": f"Todo item: '{todo.title}' completed"}

    @token_required
    def delete(self, current_user, todo_id):
        todo = Todo.query.filter_by(id=todo_id, user_id=current_user.public_id).first()
        if not todo:
            return {"message": "Todo item not found."}

        name = todo.title
        db.session.delte(todo)
        db.session.commit()
        return {"message": f'Todo item: "{name}" has been deleted'}