from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'Venue'
    
    def __init__(self , name , city , state , address , phone ,genres, image_link , facebook_link):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.genres = genres
        self.image_link = image_link
        self.facebook_link = facebook_link

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talents = db.Column(db.Boolean , default=True , nullable=False)
    shows = db.relationship('Show',backref='venue',lazy=True)
    creation_Date = db.Column(db.DateTime , nullable=False, default=datetime.utcnow)
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    def __init__(self , name , city , state , phone , genres , image_link , facebook_link):
        self.name = name
        self.city = city
        self.state = state        
        self.phone = phone
        self.genres = genres
        self.image_link = image_link
        self.facebook_link = facebook_link

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show',backref='artist',lazy=True)
    seeking_shows = db.Column(db.Boolean , default=True , nullable=False)
    creation_Date = db.Column(db.DateTime , nullable=False, default=datetime.utcnow)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    def __init__(self , artist_id , venue_id , start_Date):
       self.artist_id = artist_id
       self.venue_id = venue_id
       self.start_Date = start_Date
       
    id = db.Column(db.Integer,primary_key=True)    
    start_Date = db.Column(db.DateTime , nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)