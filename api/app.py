from flask import Flask
from flask_restful import Resource, Api
from models import *
from peewee import *
import pandas as pd

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    """
    Test code to see if the api is running
    """
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

class AllImage(Resource):
    """
    Get all heritage images
    """
    def get(self):
        images = (Images
            .select()
            .where(Images.usable == 1)
            .limit(10)
            .dicts()
            .execute())

        return [image for image in images]

api.add_resource(AllImage, '/images/all')

class InitialSuggestion(Resource):
    """
    Get five closeby heritage images 
    """
    def get(self, long, lat):
        subquery = (Locations
                    .select(Locations.street.alias('street'), fn.sqrt(fn.pow(lat-Locations.latitude, 2) + 
                                                              fn.pow(long-Locations.longitude, 2))
                            .alias('dist'),
                            Locations.longitude, Locations.latitude, Locations.radius)
                    .order_by(SQL('dist'))
                    .limit(5)
                    .alias('subquery'))
        
        images = (Images
                  .select(fn.min(Images.id).alias('id'), Images.street, Images.url, Images.title,
                          subquery.c.longitude, subquery.c.latitude, subquery.c.radius)
                  .join(subquery, on =
                        (Images.street == subquery.c.street))
                  .group_by(Images.street)
                  .where(Images.usable == 1)
                  .order_by(subquery.c.latitude)
                  .dicts()
                  .execute())
        
        return [image for image in images]
        
api.add_resource(InitialSuggestion, '/images/initial/<float:long>/<float:lat>')

class Suggestion(Resource):
    """
    Get ten suggestions based on location and previously visited images
    """
    def get(self, user_id):
        
        # get longitude and latitude of last-visited picture
        long = (UserPictures
                .select(UserPictures.location_longitude)
                .where(UserPictures.user_id==user_id)
                .order_by(UserPictures.picture_datetime)
                .limit(1)
                .dicts())

        for row in long:
            last_long = float(row['location_longitude'])

        lat = (UserPictures
                .select(UserPictures.location_latitude)
                .where(UserPictures.user_id==user_id)
                .order_by(UserPictures.picture_datetime)
                .limit(1)
                .dicts())

        for row in lat:
            last_lat = float(row['location_latitude'])
            
            
        # calculate distances from last-visited picture to each street and take 10 closest streets
        subquery_1 = (Locations
            .select(Locations.street, fn.sqrt(fn.pow(last_lat-Locations.latitude, 2) + 
                                              fn.pow(last_long-Locations.longitude, 2))
                    .alias('dist'), Locations.longitude, Locations.latitude)
            .order_by(SQL('dist'))
            .dicts()
            .limit(10)
            .alias('subquery_1'))

        top_10_streets = list(pd.DataFrame(subquery_1)['street'])
        
        # get all pictures that the user has visited before
        subquery_2 = (UserPictures
                     .select(UserPictures.image_id)
                     .where(UserPictures.user_id==user_id)
                     .dicts())
        
        # randomly assign row numbers to images within top 10 streets, but that the user has not already visited
        subquery_3 = (Locations
                    .select(fn.row_number().over(partition_by=[Locations.street], order_by=fn.Rand()).alias('rownr'),
                    Images.id, Images.street, Images.url, Images.title, Locations.longitude, Locations.latitude)
                    .where(Images.street.in_(top_10_streets) & Images.usable==1 & Images.id.not_in(subquery_2))
                    .join(Images, on=(Locations.street==Images.street))
                    .dicts()
                    .alias('subquery_4'))
        
        # select one random picture from each street in top 10 streets
        suggestions = (Images
                       .select(Images.id, Images.street, Images.title, Images.url, Images.usable, Images.year, 
                       subquery_3.c.longitude, subquery_3.c.latitude)
                       .join(subquery_3, on=(Images.id==subquery_3.c.id))
                       .where(subquery_3.c.rownr==1)
                       .order_by(subquery_3.c.latitude)
                       .dicts()
                       .execute())
        
        return [suggestion for suggestion in suggestions]

api.add_resource(Suggestion, '/images/suggestion/<int:user_id>')
          
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')