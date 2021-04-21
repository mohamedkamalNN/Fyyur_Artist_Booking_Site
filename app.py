#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
from models import Venue , Artist , Show ,  db
from sqlalchemy import desc
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config.from_object('config')
db.init_app(app) #db = SQLAlchemy(app)
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  #locale="En"
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='En')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():  
  # BONUS Requirement 2 in The Bonus Mohamed Kamal
  ven = []
  art = []
  for item  in Venue.query.order_by(desc(Venue.creation_Date)).limit(10).all():
    ven.append({'id':item.id , 'name' : item.name})
  for item  in Artist.query.order_by(desc(Artist.creation_Date)).limit(10).all():
    art.append({'id':item.id , 'name' : item.name})  
  return render_template('pages/home.html',venues=ven,artists=art)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venue_list = []
  # = Venue.query().all()
  venues_places =Venue.query.with_entities(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all() #Venue.query.group_by(Venue.city).all()
  for place in venues_places:
     venue_list = []
     venues = db.session.query(Venue).filter(Venue.state == place.state, Venue.city == place.city).all()
     for venue in venues:
       venue_list.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venue.id , Show.start_Date>datetime.now()).all()),
       })
     data.append({
       "city": place.city,
       "state": place.state,
      "venues":venue_list
     })    
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  ser = request.form.get('search_term', '')
  data = []
  venues = Venue.query.filter(Venue.name.ilike(f'%{ser}%')).all() 
  for venue in venues:   
      data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue.id , Show.start_Date > datetime.now()).all()),
      })
  response={
    "count": len(data),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id  
  past_Shows = []
  upcoming_Shows = []
  venue = Venue.query.get(venue_id)
  if venue  == None:
    flash('This Venue Could Not Be Found')
    ven = []
    art = []
    for item  in Venue.query.order_by(desc(Venue.creation_Date)).limit(10).all():
      ven.append({'id':item.id , 'name' : item.name})
    for item  in Artist.query.order_by(desc(Artist.creation_Date)).limit(10).all():
      art.append({'id':item.id , 'name' : item.name})  
    return render_template('pages/home.html',venues=ven,artists=art)
    
  genres_List = eval(venue.genres)  
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_Date<=datetime.now()).all()
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_Date>datetime.now()).all()
  for show in  past_shows_query:
     past_Shows.append({  
         "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_Date)
     })

  for show in  upcoming_shows_query:
     upcoming_Shows.append({
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_Date)
     })   
          

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": genres_List,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": "https://www.themusicalhop.com",
    "facebook_link": venue.facebook_link,
    "seeking_talents": venue.seeking_talents,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": venue.image_link,
    "past_shows": past_Shows,
    "upcoming_shows": upcoming_Shows,
    "past_shows_count": len(past_Shows),
    "upcoming_shows_count": len(upcoming_Shows),
  }  
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  if form.validate_on_submit() == False:
    for item in form.errors:
      if item == 'phone':
       flash('Please Enter A Valid Phone Number')
      elif item == 'facebook_link':
        flash('Please Enter A Valid Facebook Link')
     
    return render_template('forms/new_venue.html', form=form)
  genres_List = request.form.getlist('genres')
  new_venue = Venue(request.form['name'],request.form['city'],request.form['state'],request.form['address'],request.form['phone'],str(genres_List),'https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80',request.form['facebook_link'])
  isInserted = True
  try:
    db.session.add(new_venue)    
    db.session.commit()
  except:
    isInserted = False
    db.session.rollback()
  finally:  
    db.session.close()
  # on successful db insert, flash success
  if isInserted:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  ven = []
  art = []
  for item  in Venue.query.order_by(desc(Venue.creation_Date)).limit(10).all():
    ven.append({'id':item.id , 'name' : item.name})
  for item  in Artist.query.order_by(desc(Artist.creation_Date)).limit(10).all():
    art.append({'id':item.id , 'name' : item.name})  
  return render_template('pages/home.html',venues=ven,artists=art)

@app.route('/venues/<venue_id>/delete')
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  #Show.query.filter_by(id=venue_id).delete()
  #db.session.commit()
  shows = Show.query.filter_by(venue_id=venue_id).all()
  for show in shows:
    db.session.delete(show)
    db.session.commit()

  venue = Venue.query.get(venue_id)
  db.session.delete(venue)
 
  isInserted = True
  try:    
    db.session.commit()
  except:
    isInserted = False
    db.session.rollback()
  finally:  
    db.session.close()

  if isInserted:    
    flash('Venue '+'deleted Successfully!')
  else : 
    flash('An error occurred. Venue '+' could not be deleted.')
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  ven = []
  art = []
  for item  in Venue.query.order_by(desc(Venue.creation_Date)).limit(10).all():
    ven.append({'id':item.id , 'name' : item.name})
  for item  in Artist.query.order_by(desc(Artist.creation_Date)).limit(10).all():
    art.append({'id':item.id , 'name' : item.name})   
  return render_template('pages/home.html',venues=ven,artists=art)
  
 # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists_List = Artist.query.all()
  for item in artists_List:
    data.append({"id": item.id,"name": item.name})
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  ser = request.form.get('search_term', '')
  data = []
  artists = Artist.query.filter(Artist.name.ilike(f'%{ser}%')).all() 
  for artist in artists:   
      data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(Show.query.filter(Show.artist_id == artist.id , Show.start_Date > datetime.now()).all()),
      })
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
 
  past_Shows = []
  upcoming_Shows = []
  artist = Artist.query.get(artist_id)
  if artist == None:
    flash('This Artist Could Not Be Found')
    ven = []
    art = []
    for item  in Venue.query.order_by(desc(Venue.creation_Date)).limit(10).all():
      ven.append({'id':item.id , 'name' : item.name})
    for item  in Artist.query.order_by(desc(Artist.creation_Date)).limit(10).all():
      art.append({'id':item.id , 'name' : item.name})
    return render_template('pages/home.html',venues=ven,artists=art)

  genres_List = eval(artist.genres)  
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_Date<=datetime.now()).all()
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_Date>datetime.now()).all()
  for show in  past_shows_query:
     past_Shows.append({
        "venue_id" : show.venue_id,
        "venue_name" : show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.start_Date)
     })

  for show in  upcoming_shows_query:
     upcoming_Shows.append({
        "venue_id" : show.venue_id,
        "venue_name" : show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.start_Date)
     })   
 
 
         

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": genres_List,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_shows,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": artist.image_link,
    "past_shows": past_Shows,
    "upcoming_shows": upcoming_Shows,
    "past_shows_count": len(past_Shows) ,
    "upcoming_shows_count": len(upcoming_Shows),
  }
 
 # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist == None :
     flash('An error occurred. Artist ' + ' could not be Updated.')
     return redirect(url_for('show_artist', artist_id=artist_id))
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": eval(artist.genres),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_shows,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #"image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  if artist == None :
     flash('An error occurred. Artist ' + ' could not be Updated.')
     return redirect(url_for('show_artist', artist_id=artist_id))
  form = ArtistForm()
  if form.validate_on_submit() == False:
    for item in form.errors:
      if item == 'phone':
       flash('Please Enter A Valid Phone Number')
      elif item == 'facebook_link':
        flash('Please Enter A Valid Facebook Link')   
    return render_template('forms/edit_artist.html', form=form, artist={"id": artist.id,
    "name": artist.name,
    "genres": eval(artist.genres),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_shows,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",})    
  name = artist.name
  artist.name = request.form['name']
  artist.genres = str(request.form.getlist('genres'))
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  x = request.form.get("seeking_venue" , False)
  if x != False:
   artist.seeking_shows = True
  else:
   artist.seeking_shows = False
  #artist.image_link = request.form['image_link']

  isInserted = True
  try:    
    db.session.commit()
  except:
    isInserted = False
    db.session.rollback()
  finally:  
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  if isInserted:    
    flash('Artist ' + name + ' was successfully Updated!')
  else : 
    flash('An error occurred. Artist ' + name + ' could not be Updated.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue == None :
     flash('An error occurred. Venue '+ ' could not be Updated.')
     return redirect(url_for('show_venue', venue_id=venue_id))

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": eval(venue.genres),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": "https://www.themusicalhop.com",
    "facebook_link": venue.facebook_link,
    "seeking_talents": venue.seeking_talents,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #"image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if form.validate_on_submit() == False:
    for item in form.errors:
      if item == 'phone':
       flash('Please Enter A Valid Phone Number')
      elif item == 'facebook_link':
        flash('Please Enter A Valid Facebook Link')   
    return render_template('forms/edit_venue.html', form=form, venue={
    "id": venue.id,
    "name": venue.name,
    "genres": eval(venue.genres),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": "https://www.themusicalhop.com",
    "facebook_link": venue.facebook_link,
    "seeking_talents": venue.seeking_talents,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #"image_link": venue.image_link
  })
 # venue = Venue.query.get(venue_id)
  name = venue.name
  venue.name = request.form['name']
  venue.genres = str(request.form.getlist('genres'))
  venue.address = request.form['address']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.phone = request.form['phone']
  venue.facebook_link = request.form['facebook_link']  
  x = request.form.get("seeking_talents" , False)
  if x != False:
   venue.seeking_talents = True
  else:
   venue.seeking_talents = False
  #artist.image_link = request.form['image_link']

  isInserted = True
  try:    
    db.session.commit()
  except:
    isInserted = False
    db.session.rollback()
  finally:  
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  if isInserted:    
    flash('Venue ' + name + ' was successfully Updated!')
  else : 
    flash('An error occurred. Venue ' + name + ' could not be Updated.')
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
  # TODO: insert form data as a new Venue record in the db, instead.
  form = ArtistForm()
  if form.validate_on_submit() == False:
    for item in form.errors:
      if item == 'phone':
       flash('Please Enter A Valid Phone Number')
      elif item == 'facebook_link':
        flash('Please Enter A Valid Facebook Link')
     
    return render_template('forms/new_artist.html', form=form)

  genres_List = request.form.getlist('genres')
  new_artist = Artist(request.form['name'],request.form['city'],request.form['state'],request.form['phone'],str(genres_List),'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80',request.form['facebook_link'])
  # Java script Validation IS Bouns
  isInserted = True
  try:
    db.session.add(new_artist)    
    db.session.commit()
  except:
    isInserted = False
    db.session.rollback()
  finally:  
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  if isInserted:    
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else : 
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  ven = []
  art = []
  for item  in Venue.query.order_by(desc(Venue.creation_Date)).limit(10).all():
    ven.append({'id':item.id , 'name' : item.name})
  for item  in Artist.query.order_by(desc(Artist.creation_Date)).limit(10).all():
    art.append({'id':item.id , 'name' : item.name})
  return render_template('pages/home.html',venues=ven,artists=art)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.all()
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id ,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_Date)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist = Artist.query.get(request.form['artist_id'])
  venue = Venue.query.get(request.form['venue_id'])
  if artist == None :
     flash('An error occurred. Artist ' + ' could not be Updated.')
     return redirect(url_for('create_show_submission'))
  if venue == None :
     flash('An error occurred. Venue '  + ' could not be Updated.')
     return redirect(url_for('create_show_submission'))   

  ven = []
  art = []
  for item  in Venue.query.order_by(desc(Venue.creation_Date)).limit(10).all():
    ven.append({'id':item.id , 'name' : item.name})
  for item  in Artist.query.order_by(desc(Artist.creation_Date)).limit(10).all():
    art.append({'id':item.id , 'name' : item.name})   

  if artist.seeking_shows != True:
    flash('This Artist Does not Seeking Any Shows Right Now!')
    return render_template('pages/home.html',venues=ven,artists=art)

  if venue.seeking_talents != True:
    flash('This Venue Does not Seeking Any Shows Right Now!')
    return render_template('pages/home.html',venues=ven,artists=art)

  new_Show = Show(request.form['artist_id'],request.form['venue_id'],request.form['start_time'])
  
  isInserted = True
  try:
    db.session.add(new_Show)    
    db.session.commit()
  except:
    isInserted = False
    db.session.rollback()
  finally:  
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  if isInserted:    
    flash('Show was successfully listed!')
  else : 
    flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html',venues=ven,artists=art)

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
