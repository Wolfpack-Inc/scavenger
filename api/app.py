from flask import Flask
from flask_restful import Resource, Api
from models import *
from peewee import *

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
                    .select(Locations.street.alias('street'), fn.sqrt(fn.pow(lat-Locations.dis_lat, 2) + 
                                                              fn.pow(long-Locations.dis_long, 2))
                            .alias('dist'),
                            Locations.dis_long, Locations.dis_lat)
                    .order_by(SQL('dist'))
                    .limit(5)
                    .alias('subquery'))
        
        images = (Images
                  .select(fn.min(Images.id).alias('id'), Images.street, Images.url, Images.title,
                          subquery.c.dis_long, subquery.c.dis_lat)
                  .join(subquery, on =
                        (Images.street == subquery.c.street))
                  .group_by(Images.street)
                  .where(Images.usable == 1)
                  .dicts()
                  .execute())
        
        return [image for image in images]
        
api.add_resource(InitialSuggestion, '/images/initial/<float:long>/<float:lat>')
          
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')