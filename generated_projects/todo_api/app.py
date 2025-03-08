from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress warning
db = SQLAlchemy(app)


# Define the Todo model
class Todo(db.Model):
    """
    Represents a todo item in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Todo {self.id}: {self.task}>'


# Create the database tables (if they don't exist)
with app.app_context():
    db.create_all()


# API Routes
@app.route('/todos', methods=['GET'])
def get_todos():
    """
    Retrieves all todo items from the database.

    Returns:
        A JSON list of todo items.
    """
    todos = Todo.query.all()
    todo_list = [{'id': todo.id, 'task': todo.task, 'completed': todo.completed} for todo in todos]
    return jsonify(todo_list)


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """
    Retrieves a specific todo item by ID.

    Args:
        todo_id: The ID of the todo item to retrieve.

    Returns:
        A JSON representation of the todo item, or a 404 error if not found.
    """
    todo = Todo.query.get_or_404(todo_id)
    return jsonify({'id': todo.id, 'task': todo.task, 'completed': todo.completed})


@app.route('/todos', methods=['POST'])
def create_todo():
    """
    Creates a new todo item.

    Request body should contain a JSON object with a 'task' field.

    Returns:
        A JSON representation of the newly created todo item.
    """
    task = request.json.get('task')
    if not task:
        return jsonify({'error': 'Task is required'}), 400

    new_todo = Todo(task=task)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'id': new_todo.id, 'task': new_todo.task, 'completed': new_todo.completed}), 201


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """
    Updates an existing todo item.

    Args:
        todo_id: The ID of the todo item to update.

    Request body should contain a JSON object with the fields to update (e.g., 'task', 'completed').

    Returns:
        A JSON representation of the updated todo item, or a 404 error if not found.
    """
    todo = Todo.query.get_or_404(todo_id)

    task = request.json.get('task')
    completed = request.json.get('completed')

    if task:
        todo.task = task
    if completed is not None:  # Handle boolean values correctly
        todo.completed = completed

    db.session.commit()

    return jsonify({'id': todo.id, 'task': todo.task, 'completed': todo.completed})


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """
    Deletes a todo item.

    Args:
        todo_id: The ID of the todo item to delete.

    Returns:
        A 204 No Content response on success, or a 404 error if not found.
    """
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    
