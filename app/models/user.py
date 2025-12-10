from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @classmethod
    def get_by_id(cls, user_id):
        with db.get_cursor() as cur:
            cur.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if row:
                return cls(row['id'], row['username'], row['password_hash'])
        return None

    @classmethod
    def get_by_username(cls, username):
        with db.get_cursor() as cur:
            cur.execute("SELECT * FROM Users WHERE username = %s", (username,))
            row = cur.fetchone()
            if row:
                return cls(row['id'], row['username'], row['password_hash'])
        return None

    @classmethod
    def create(cls, username, password):
        hashed_pw = generate_password_hash(password)
        with db.get_cursor() as cur:
            cur.execute(
                "INSERT INTO Users (username, password_hash) VALUES (%s, %s) RETURNING id",
                (username, hashed_pw)
            )
            return cur.fetchone()['id']

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)