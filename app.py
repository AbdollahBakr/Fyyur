#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
import logging
from flask_moment import Moment
from flask_wtf import Form
from forms import *
from sqlalchemy import text, desc
from psycopg2.extras import Json
from logging import ( 
  Formatter, 
  FileHandler
)
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for
) 
from models import (
  Show, 
  Venue, 
  Artist, 
  db
)


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config.DatabaseURI')
app.config['SECRET_KEY'] = 'KJSDF3232jflsdkas'
db.init_app(app)


# Database fyyur has been created using psql
# Connection URI has been set in "config.py" to connect to fyyur database
# MIGRATION PART
from flask_migrate import Migrate
migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # Could be implemented to display recent venues usnig join (Venue, Show)
  venues = Venue.query.limit(10).all()
  artists = Artist.query.limit(10).all()
  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  areas = db.session.query(Venue.city, Venue.state).distinct().all()
  data = []
  for a in areas:
      # Fetch area (city, state)
      city = a[0]
      state = a[1]
      venues = []

      # Fetch venues
      # RAW SQL
      # sql = 'SELECT id, name FROM venues WHERE city = :city AND state = :state'
      # vens_per_area = db.engine.execute(text(sql), city=city, state=state).fetchall()
      vens_per_area = Venue.query.filter(Venue.city == city, Venue.state == state).all()
      for venue in vens_per_area:
          venues.append({
              'id': venue.__dict__['id'], 
              'name': venue.__dict__['name']})
      
      # Append to the data array
      data.append({'city': city, 'state': state, 'venues': venues})

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term') 
  
  # RAW SQL
  # filtered = db.engine.execute('SELECT * FROM venues WHERE LOWER(name) LIKE LOWER(%s)', f'%{search_term}%').fetchall()
  
  filtered = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  response={
    "count": len(list(filtered)),
    "data": filtered
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  # USING RAW SQL
  # venue = db.engine.execute(text('select * from venues where id=:id'), id=venue_id).fetchone()
  # upcoming_sql = 'SELECT artist_id, venue_id, name as artist_name, image_link as artist_image_link, start_time FROM shows JOIN artists ON venue_id = :venue_id AND id = artist_id WHERE start_time > now()'
  # past_sql = 'SELECT artist_id, venue_id, name as artist_name, image_link as artist_image_link, start_time FROM shows JOIN artists ON venue_id = :venue_id AND id = artist_id WHERE start_time < now()'
  # upcoming_shows_list = db.engine.execute(text(upcoming_sql), venue_id=venue_id).fetchall()
  # past_shows_list = db.engine.execute(text(past_sql), venue_id=venue_id).fetchall()
  # # convert to dict
  # upcoming_shows = []
  # for show in upcoming_shows_list:
  #   upcoming_shows.append(dict(show))

  # past_shows = []
  # for show in upcoming_shows_list:
  #   past_shows.append(dict(show))
  # venue = dict(venue)

  # USING SQL ALCHEMY
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
  venue = venue.__dict__
  
  upcoming_shows = db.session.query(Show).join(Venue).filter(Venue.id == venue_id, Venue.id == Show.venue_id, Show.start_time > datetime.now()).all()
  past_shows = db.session.query(Show).join(Venue).filter(Venue.id == venue_id, Venue.id == Show.venue_id, Show.start_time < datetime.now()).all()

  # appending upcoming and past shows to data
  venue['upcoming_shows'] = upcoming_shows
  venue['upcoming_shows_count'] = len(upcoming_shows)
  venue['past_shows'] = past_shows
  venue['past_shows_count'] = len(past_shows)

  return render_template('pages/show_venue.html', venue=venue)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate_on_submit():
    try:
      venue = Venue()
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

    except ValueError as e:
        print(e)
        flash('An error occured! Make sure to follow the input rules.', 'error')
        db.session.rollback()
    finally:
        db.session.close()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term') 
  filtered = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  
  response={
    "count": len(list(filtered)),
    "data": filtered
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
  artist = artist.__dict__
  
  upcoming_shows = db.session.query(Show).join(Artist).filter(Artist.id == artist_id, Artist.id == Show.artist_id, Show.start_time > datetime.now()).all()
  past_shows = db.session.query(Show).join(Artist).filter(Artist.id == artist_id, Artist.id == Show.artist_id, Show.start_time < datetime.now()).all()

  artist['upcoming_shows'] = upcoming_shows
  artist['upcoming_shows_count'] = len(upcoming_shows)
  artist['past_shows'] = past_shows
  artist['past_shows_count'] = len(past_shows)
  
  return render_template('pages/show_artist.html', artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  # REMOVE
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  # REMOVE
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      artist = Artist()
      form.populate_obj(artist)
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

    except ValueError as e:
        print(e)
        flash('An error occured! Make sure to follow the input rules.', 'error')
        db.session.rollback()
    finally:
        db.session.close()

  return render_template('forms/new_artist.html', form=form)
    
"""   
  USING RAW SQL

  form_name = request.form.get("name")
  form_city = request.form.get("city")
  form_state = request.form.get("state")
  form_phone = request.form.get("phone")
  form_genres = request.form.getlist("genres") # Cast to Json(), if using raw sql
  form_facebook_link = request.form.get("facebook_link")

  sql = 'INSERT INTO artists(name, city, state, phone, genres, facebook_link) VALUES(:name, :city, :state, :phone, :genres, :facebook_link)'
  db.engine.execute(
    text(sql), 
    name=form_name, 
    city=form_city, 
    state=form_state, 
    phone=form_phone, 
    genres=form_genres, 
    facebook_link=form_facebook_link) 
"""
  
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  for s in Show.query.all():
      data.append({
          "venue_id": s.venue_id,
          "venue_name": s.venue.name,
          "artist_id": s.artist_id,
          "artist_name": s.artist.name,
          "artist_image_link": s.artist.image_link,
          "start_time": str(s.start_time)
      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form)
  if form.validate_on_submit():
    try:
      show = Show()
      form.populate_obj(show)
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was created successfully!')
      return render_template('pages/home.html')

    except ValueError as e:
        print(e)
        flash('An error occured! Make sure to follow the input rules.', 'error')
        db.session.rollback()
    finally:
        db.session.close()

  return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
