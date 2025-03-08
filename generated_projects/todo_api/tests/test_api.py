"""Tests for the API endpoints (create, read, update, delete todos)."""

import unittest
import json
from app import app, db  # Import your Flask app and models

class APITestCase(unittest.TestCase):
    """Test case for the API endpoints."""

    def setUp(self):
        """Set up the test environment."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory database for testing
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        """Tear down the test environment."""
        db.session.remove()
        db.drop_all()

    def create_todo(self, task):
        """Helper function to create a todo."""
        return self.app.post('/todos', data=json.dumps(dict(task=task)), content_type='application/json')

    def get_todos(self):
        """Helper function to get all todos."""
        return self.app.get('/todos')

    def get_todo(self, todo_id):
        """Helper function to get a specific todo."""
        return self.app.get(f'/todos/{todo_id}')

    def update_todo(self, todo_id, task, completed=None):
        """Helper function to update a todo."""
        data = dict(task=task)
        if completed is not None:
            data['completed'] = completed
        return self.app.put(f'/todos/{todo_id}', data=json.dumps(data), content_type='application/json')

    def delete_todo(self, todo_id):
        """Helper function to delete a todo."""
        return self.app.delete(f'/todos/{todo_id}')

    def test_create_todo(self):
        """Test creating a new todo."""
        response = self.create_todo("Buy groceries")
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['task'], "Buy groceries")
        self.assertFalse(data['completed'])

    def test_get_todos(self):
        """Test getting all todos."""
        self.create_todo("Buy groceries")
        self.create_todo("Walk the dog")
        response = self.get_todos()
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data), 2)

    def test_get_todo(self):
        """Test getting a specific todo."""
        create_response = self.create_todo("Buy groceries")
        create_data = json.loads(create_response.data.decode('utf-8'))
        todo_id = create_data['id']

        response = self.get_todo(todo_id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['task'], "Buy groceries")

    def test_get_todo_not_found(self):
        """Test getting a todo that doesn't exist."""
        response = self.get_todo(999)  # Non-existent ID
        self.assertEqual(response.status_code, 404)

    def test_update_todo(self):
        """Test updating a todo."""
        create_response = self.create_todo("Buy groceries")
        create_data = json.loads(create_response.data.decode('utf-8'))
        todo_id = create_data['id']

        response = self.update_todo(todo_id, "Buy milk", completed=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['task'], "Buy milk")
        self.assertTrue(data['completed'])

    def test_update_todo_not_found(self):
        """Test updating a todo that doesn't exist."""
