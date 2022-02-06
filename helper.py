# THIS FILE IS JUST FOR PRACTICE


from models import Venue, Artist, Show

# from app import db
import datetime, time

# Convert sqlalchemy object to dict:
# Reference: https://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
def row_to_dic(row):
    d = {}
    for c in row.__table__.columns:
        d[c.name] = getattr(row, c.name)
    return d

# one liner version
# row2dic = lambda r: {c.name: getattr(r, c.name) for c in r.__table__.columns}

# row = db.session.query(Venue).first()

# data = Venue.query.join(Show).join(Artist)
# data = []
# for s in Show.query.all():
#     data.append({
#         "venue_id": s.venue_id,
#         "venue_name": s.venue.name,
#         "artist_id": s.artist_id,
#         "artist_name": s.artist.name,
#         "artist_image_link": s.artist.image_link,
#         "start_time": s.start_time
#     })

# print(data)

# Venue.query.with_entities(Venue.name).all()
# areas = db.session.query(Venue.city, Venue.state).distinct().all()
# areas = Venue.query.all()
# data = []
# for a in areas:
#     a_dic = a.__dict__
#     city = a_dic['city']
#     state = a_dic['state']

#     venues = []
#     vens_per_area = Venue.query.filter(Venue.city==city, Venue.state==state).all()
#     for venue in vens_per_area:
#         venues.append({
#             'id': venue.__dict__['id'], 
#             'name': venue.__dict__['name']})
    
#     data.append({'city': city, 'state': state, 'venues': venues})

# print(areas)
# areas = Venue.query.filter(Venue.id==1).all()


# TO COMPLETE

from sqlalchemy import create_engine, inspect, text
from config import SQLALCHEMY_DATABASE_URI as uri
engine = create_engine(uri)
# result = engine.execute('SELECT id, name FROM venues WHERE id =7').fetchall()

# inspector = inspect(engine).get_columns('shows')
# result2 = Show.query.all()
# for r in result:
#     print(dict(r.items())) #convert tuples to dictionary

# cmd = 'SELECT id, name FROM venues WHERE city = :city AND state = :state'
# city = 'Nozha'
# state = 'CA'
# exc = engine.execute(text(cmd), city=city, state=state).fetchall()
# print(**{'id': 1, 'title': 'habbit'})

exc = engine.execute(text('select * from venues where id=:id'), id=7).fetchone()
# exc = engine.execute(text('select * from venues join shows on id = :venue_id where start_time <= now()'), venue_id=7).fetchone()
data = dict(exc)
upcoming_shows = engine.execute(text('SELECT artist_id, venue_id, name as artist_name, image_link as artist_image_link, start_time FROM shows JOIN artists ON venue_id = :venue_id AND id = artist_id WHERE start_time < now()'), venue_id=7).fetchall()

print(len(upcoming_shows))
# print(upcoming_shows)
