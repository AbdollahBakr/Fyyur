from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# The nature of the relationship between Venue and Artist is many-to-many, exemplified in the Show as an association table/object.
# Each association between the Artist and the Venue is actually a Show

db = SQLAlchemy()

class Show(db.Model):
  __tablename__ = 'shows'

  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)
  start_time = db.Column(db.DateTime, primary_key=True) 
  artist = db.relationship('Artist', back_populates='venues')
  venue = db.relationship('Venue', back_populates='artists')


class Venue(db.Model):
    __tablename__ = 'venues'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    artists = db.relationship('Show', back_populates='venue')
    
    # additional/missing fields
    genres = db.Column(db.JSON, default={})
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    

    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.facebook_link}>'


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    venues = db.relationship('Show', back_populates='artist')

    # additional/missing fields
    genres = db.Column(db.JSON, default={})
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
