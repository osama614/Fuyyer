from flask_sqlalchemy import SQLAlchemy

from app import app

db = SQLAlchemy(app)




class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True ,unique=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    seeking_description = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.String(), default=False)
    website = db.Column(db.String())
    # the relationship between Show TAble and Venue TAble is one to many
    shows_ven = db.relationship('Show', backref='venue')


class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120),nullable=False )  
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String())
    seeking_venue = db.Column(db.String(), default=False)
    seeking_description = db.Column(db.String(200))
    website = db.Column(db.String())
    # the relationship between Show TAble and Artist TAble is one to many
    shows_art = db.relationship('Show', backref='artist')
    

class Show(db.Model):
  __tablename__='show'
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
  start_time = db.Column(db.String(), nullable=False)