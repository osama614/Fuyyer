#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
# importing that module for the upcoming and past shows condition.
from datetime import datetime
import json
import dateutil.parser
import babel
from flask import (Flask,
      render_template,
      request,
      Response,
      flash, redirect, 
      url_for)

from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# that module to migrate data and have a script for my modificatoins.
from flask_migrate import Migrate




#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  data = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  
  data1=[]
  for venue_data in data:
      city_name = venue_data[0]
      city_state = venue_data[1]
      get_data = db.session.query(Venue).filter(Venue.city == city_name, Venue.state == city_state)
      group = {
          "city": city_name,
          "state": city_state,
          "venues": []
      }
      venues = get_data.all()
      for venue in venues:
          
          group['venues'].append({
              "id": venue.id,
              "name": venue.name
          })
      data1.append(group)
  
  return render_template('pages/venues.html', areas=data1)

@app.route('/venues/search', methods=['POST'])
def search_venues():
 
  search_term=request.form.get('search_term', '')
  get_data = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  # get_data = Venue.query.filter(Venue)msearch(search_term).all()
  nums = len(get_data)
  response = {
    "count" : nums,
    "data" : []
  } 
  for num in get_data:
    response["data"].append({
      "id" : num.id,
      "name" :num.name
    })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  
  # Get data from Venues Table by given id 
 
  m = venue_id
  venues = Venue.query.filter(Venue.id==m).all()
  for venue in venues:
    data1 = {
      "id" : venue.id,
    "name" : venue.name,
    "city" : venue.city,
    "state" : venue.state,
    "phone" : venue.phone,
    "seeking_talent" : venue.seeking_talent,
    "seeking_description" : venue.seeking_description,
    "image_link" : venue.image_link,
    "facebook_link" : venue.facebook_link,
    "genres" : venue.genres,
    "website" : venue.website,
    "address" : venue.address,
    "upcoming_shows" : [],
    "past_shows" : []
    } 
   
    shows = db.session.query(Artist.image_link, Artist.name, Show.start_time, Show.artist_id).filter(Show.venue_id==m,
         Artist.id==Show.artist_id).all()
    for show in shows:
      artist_image_link = show[0]
      artist_name = show[1]
      start_time = show[2]
      artist_id = show[3]
    
      time = datetime.strptime(start_time,"%Y-%m-%d %H:%M:%S")
      now = datetime.now()
      # this condition to add the shows whose time in the future
      # to upcoming_shows and that past to past_shows
      if time > now:
        data1['upcoming_shows'].append({
          "artist_image_link" : artist_image_link,
          "artist_name" : artist_name,
          "start_time" : start_time,
          "artist_id" : artist_id
        })
        num = len(data1.get("upcoming_shows"))
        data1["upcoming_shows_count"] = num
      else:
        data1['past_shows'].append({
          "artist_image_link" : artist_image_link,
          "artist_name" : artist_name,
          "start_time" : start_time,
          "artist_id" : artist_id
        })
        num = len(data1.get("past_shows"))
        data1["past_shows_count"] = num
  
 
  return render_template('pages/show_venue.html', venue=data1)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  
  # Gitting the data from the forms and store them in thire Columns
  error = False
  try:
      name = request.form.get('name')
      city = request.form.get('city')
      address = request.form.get('address')
      genres = request.form.getlist('genres')
      state = request.form.get('state')
      facebook_link = request.form.get('facebook_link','')
      phone = request.form.get('phone')
      image_link = request.form.get('image_link')
      website = request.form.get('website')
      seeking_talent = request.form.get('seeking_talent')
      seeking_description = request.form.get('seeking_description')
      venues = Venue(name=name, city=city, address=address, genres=genres, state=state, facebook_link=facebook_link,
        phone=phone, image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
              
      db.session.add(venues)
      db.session.commit()
  
  except:
      error = True
      db.session.rollback()    
      flash('Venue ' + request.form['name'] + ' was unsuccessfully listed!')
      return render_template('pages/home.html') 
  finally:
      db.session.close()
  if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
# collect the venue that will daleted by its id 
   try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
   except:
        db.session.rollback()
   finally:
        db.session.close()
   return None        
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  # show all artists on data
  data = Artist.query.all()
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term=request.form.get('search_term', '')
  get_data = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  nums = len(get_data)
  response = {
    "count" : nums,
    "data" : []
  } 
  for num in get_data:
    response["data"].append({
      "id" : num.id,
      "name" :num.name
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  
  m = artist_id
  artists = Artist.query.filter(Artist.id==m).all()
  for artist in artists:
    
    data1 = {
      "id" : artist.id,
    "name" : artist.name,
    "city" : artist.city,
    "state" : artist.state,
    "phone" : artist.phone,
    "seeking_venue" : artist.seeking_venue,
    "seeking_description" : artist.seeking_description,
    "image_link" : artist.image_link,
    "facebook_link" : artist.facebook_link,
    "genres" : artist.genres,
    "website" : artist.website,
    "upcoming_shows" : [],
    "past_shows" : []
    } 
    
    shows = db.session.query(Venue.image_link, Venue.name, Show.start_time, Show.venue_id).filter(Show.artist_id==m,
         Venue.id==Show.venue_id  ).all()
    for show in shows:
      venue_image_link = show[0]
      venue_name = show[1]
      start_time = show[2]
      venue_id = show[3]
    
      time = datetime.strptime(start_time,"%Y-%m-%d %H:%M:%S")
      now = datetime.now()
      
      if time > now:
        data1['upcoming_shows'].append({
          "venue_image_link" : venue_image_link,
          "venue_name" : venue_name,
          "start_time" : start_time,
          "venue_id" : venue_id
        })
        num = len(data1.get("upcoming_shows"))
        data1["upcoming_shows_count"] = num
      else:
        data1['past_shows'].append({
          "venue_image_link" : venue_image_link,
          "venue_name" : venue_name,
          "start_time" : start_time,
          "venue_id" : venue_id
        })
        num = len(data1.get("past_shows"))
        data1["past_shows_count"] = num
    
  return render_template('pages/show_artist.html', artist=data1)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  # artist record with ID <artist_id> using the new attributes
  try:
      name = request.form.get('name')
      city = request.form.get('city')
      genres = request.form.getlist('genres')
      state = request.form.get('state')
      facebook_link = request.form.get('facebook_link','')
      phone = request.form.get('phone')
      image_link = request.form.get('image_link')
      website = request.form.get('website')
      seeking_venue = request.form.get('seeking_venue')
      seeking_description = request.form.get('seeking_description')
      artist = Artist.query.get( artist_id)
      artist.name = name
      artist.city = city
      artist.genres = genres
      artist.state = state
      artist.facebook_link = facebook_link
      artist.phone = phone 
      artist.image_link = image_link
      artist.website = website
      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description
      db.session.commit()
  except:
      
      db.session.rollback()    
      flash('Artist ' + request.form['name'] + ' was unsuccessfully edited!')
      return redirect(url_for('show_artist', artist_id=artist_id))
  finally:
      db.session.close()
  
  flash('Artist ' + request.form['name'] + ' was successfully edited!')    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
 
  # collect all venue data to can modify it
  venue = db.session.query(Venue).get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  try:
      name = request.form.get('name')
      city = request.form.get('city')
      address = request.form.get('address')
      genres = request.form.getlist('genres')
      state = request.form.get('state')
      facebook_link = request.form.get('facebook_link','')
      phone = request.form.get('phone')
      image_link = request.form.get('image_link')
      website = request.form.get('website')
      seeking_talent = request.form.get('seeking_talent')
      seeking_description = request.form.get('seeking_description')
      venue = Venue.query.get( venue_id)
      venue.name = name
      venue.city = city
      venue.address = address
      venue.genres = genres
      venue.state = state
      venue.facebook_link = facebook_link
      venue.phone = phone 
      venue.image_link = image_link
      venue.website = website
      venue.seeking_talent = seeking_talent
      venue.seeking_description = seeking_description
      db.session.commit()
  except:
      
      db.session.rollback()    
      flash('Venue ' + request.form['name'] + ' was unsuccessfully listed!')
      return redirect(url_for('show_venue', venue_id=venue_id))
  finally:
      db.session.close()
  
  flash('Venue ' + request.form['name'] + ' was successfully listed!')   
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  
  error = False
  try:
      name = request.form.get('name')
      city = request.form.get('city')
      genres = request.form.getlist('genres')
      state = request.form.get('state')
      facebook_link = request.form.get('facebook_link','')
      image_link = request.form.get('image_link','')
      phone = request.form.get('phone')
      seeking_venue = request.form.get('seeking_venue')
      website = request.form.get('website')
      seeking_description = request.form.get('seeking_description')
      artists = Artist(name=name, city=city, genres=genres, state=state, facebook_link=facebook_link,phone=phone,
       image_link=image_link, seeking_venue=seeking_venue, website=website, seeking_description=seeking_description)

      db.session.add(artists)
      db.session.commit()
  except:
      error = True
      db.session.rollback()    
      flash('Artist ' + request.form['name'] + ' was unsuccessfully listed!')
      return render_template('pages/home.html')
 
  finally:
      db.session.close()

  if not error:
      
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  # collect the shows data by conditions and its relationship with Artist table and Venue table. 
  nams = db.session.query(Venue.name, Artist.name,
          Show.start_time, Show.artist_id,Show.venue_id, Artist.image_link).filter(Venue.id==Show.venue_id, Artist.id==Show.artist_id)

  data1=[]
  for name in nams:
      venue_name = name[0]
      artist_name = name[1]
      start_time = name[2]
      art_id = name[3]
      ven_id = name[4]
      image = name[5]
          
      data = {
          "venue_name": venue_name,
          "artist_name": artist_name,
          "artist_id" : art_id,
          "venue_id" : ven_id,
          "start_time" : start_time,
          "artist_image_link" : image

      }
      data1.append(data)
  return render_template('pages/shows.html', shows=data1)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  
        venue_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')
        artist_id = request.form.get('artist_id')
        show = Show(start_time=start_time,artist_id=artist_id,venue_id=venue_id)
        catch_errors = db.session.query(Venue.id, Artist.id).all()
        for catch_error in catch_errors:
          ven_id = catch_error[0]
          art_id = catch_error[1]
          if int(venue_id) == ven_id and int(artist_id) == art_id:
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
            return render_template('pages/home.html')
        if int(venue_id) != ven_id or int(artist_id) != art_id :
            flash('Show was unsuccessfully listed!')
            return render_template('pages/home.html')
      

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
