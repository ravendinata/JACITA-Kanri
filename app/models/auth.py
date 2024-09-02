from sqlalchemy.sql import func

from app.extensions import db

class Users(db.Model):
    # Meta Attributes
    date_added = db.Column(db.DateTime, server_default = func.now())
    date_modified = db.Column(db.DateTime, server_default = func.now(), onupdate = func.now())

    # User Attributes
    username = db.Column(db.String(24), primary_key = True)
    password = db.Column(db.String(32))
    email = db.Column(db.String(100))
    role = db.Column(db.String(45))
    status = db.Column(db.String(45), default = 'Active')

    def __repr__(self):
        return f"<User: {self.username}>"
    
    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }