from flask.globals import session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), unique=False, nullable=False)
    last_name = db.Column(db.String(120), unique=False, nullable=False)
    phone_number = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    salt = db.Column(db.String(80),nullable=False)


    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "email": self.email,
            "salt":self.salt
            # do not serialize the password, its a security breach
        }
    
    def update(self, ref_user):
        if "first_name" in ref_user:
            self.first_name = ref_user["first_name"]
        if "last_name" in ref_user:
            self.last_name = ref_user["last_name"]
        if "phone_number" in ref_user:
            self.phone_number = ref_user["phone_number"]
        try:
            db.session.commit()
            return True
        except Exception as error:
            db.session.rollback()
            return False
    
    @classmethod
    def create(cls, ref_user):
        try:
            new_user = cls(**ref_user)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as error:
            db.session.rollback()
            print(error)
            return None
