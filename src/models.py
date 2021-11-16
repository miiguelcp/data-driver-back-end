from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from datetime import timezone, datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), unique=False, nullable=False)
    last_name = db.Column(db.String(120), unique=False, nullable=False)
    phone_number = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    salt = db.Column(db.String(80),nullable=False)
    travels = db.relationship('Travel', backref='user', uselist=True)

    def serialize(self):
        return {
            "first_name": self.first_name,
            "id": self.id,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "email": self.email,
            "salt":self.salt,
        }
            # do not serialize the password, its a security breach
        
    
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
            print(ref_user)
            new_user = cls(**ref_user)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as error:
            db.session.rollback()
            print(error)
            return None

class Travel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    initial_amount = db.Column(db.Integer, unique=False, nullable=False)
    lodging = db.Column(db.Integer, unique=False, nullable=False)
    food = db.Column(db.Integer, unique=False, nullable=False)
    fuel = db.Column(db.Integer, unique=False, nullable=False)
    toll = db.Column(db.Integer, nullable=False)
    unexpected = db.Column(db.Integer,nullable=False)  
    date = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda : datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    __table_args__= (db.UniqueConstraint(
        'user_id',
        'id',
        name = "unique_travel_for_user" 
    ),)

    def serialize(self):
        return {
            "initial_amount": self.initial_amount,
            "id": self.id,
            "lodging": self.lodging,
            "food": self.food,
            "fuel": self.fuel,
            "toll":self.toll,
            "unexpected": self.unexpected,
            "date" : self.date
        }
        


    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
            return True
        except Exception as error:
            db.session.rollback()
            return False
