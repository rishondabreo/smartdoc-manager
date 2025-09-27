# models/user.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

# Simple in-memory user store (replace with Firestore/Datastore for production)
users_db = {
    '1': User('1', 'admin', 'admin@smartdoc.com')
}