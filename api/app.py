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
                    .select(Locations.street, fn.sqrt(fn.pow(lat-Locations.latitude, 2) + 
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
        last_visited = (UserPictures
                        .select(fn.max(UserPictures.picture_datetime))
                        .where(UserPictures.user_id==user_id))

        long = (UserPictures
                .select(UserPictures.location_longitude)
                .where(UserPictures.user_id==user_id & UserPictures.picture_datetime==last_visited)
                .dicts())

        lat = (UserPictures
                .select(UserPictures.location_latitude)
                .where(UserPictures.user_id==user_id & UserPictures.picture_datetime==last_visited)
                .dicts())

        subquery_2 = (Locations
                      .select(Locations.street, fn.sqrt(fn.pow(long-Locations.latitude, 2) + 
                                                        fn.pow(lat-Locations.longitude, 2))
                              .alias('dist'), Locations.longitude, Locations.latitude)
                      .order_by(SQL('dist'))
                      .dicts()
                      .limit(10)
                      .alias('subquery_2'))

        top_10_streets = list(pd.DataFrame(subquery_1)['street'])

        subquery_3 = (UserPictures
                      .select(UserPictures.image_id)
                      .where(UserPictures.user_id==user_id)
                      .dicts())

        subquery_4 = (Locations
                      .select(fn.row_number().over(partition_by=[Locations.street], order_by=fn.Rand()).alias('rownr'),
                            Images.id, Images.street, Images.url, Images.title, Locations.longitude, Locations.latitude)
                      .where(Images.street.in_(top_10_streets) & Images.usable==1 & Images.id.not_in(subquery_3))
                      .join(Images, on=(Locations.street==Images.street))
                      .dicts()
                      .alias('subquery_4'))

        suggestions = (Images
                       .select()
                       .join(subquery_4, on=(Images.id==subquery_4.c.id))
                       .where(subquery_4.c.rownr==1)
                       .order_by(subquery_4.c.latitude)
                       .dicts()
                       .execute())
        
        return [suggestion for suggestion in suggestions]

api.add_resource(Suggestion, '/images/suggestion/<int:user_id>')
          
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')