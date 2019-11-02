from flask import Flask
from flask_restful import Resource, Api
from models import *
from peewee import *
import pandas as pd
from datetime import date, datetime, timedelta
from playhouse.shortcuts import model_to_dict

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    """
    Test code to see if the api is running
    """
    def get(self):
        return {'ni hao': 'world'}

api.add_resource(HelloWorld, '/')

class SessionPoints(Resource):
    """
    Returns points collected by a user in today's session
    """
    def get(self, user_id):
        today = date.today()

        image_ids = (UserPictures
                    .select(UserPictures.image_id)
                    .where((UserPictures.user_id == user_id) and (UserPictures.picture_datetime > today))
                    .dicts()
                    .execute())
        
        image_ids_list = [image_id['image'] for image_id in image_ids]

        points = (Images
                .select(Images.points)
                .where(Images.id.in_(image_ids_list))
                .dicts()
                .execute())
        
        return {'points' :sum([point['points'] for point in points])}
    
api.add_resource(SessionPoints, '/session-points/<string:user_id>')

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
                .order_by(UserPictures.picture_datetime.desc())
                .limit(1)
                .dicts())

        for row in long:
            last_long = float(row['location_longitude'])

        lat = (UserPictures
                .select(UserPictures.location_latitude)
                .where(UserPictures.user_id==user_id)
                .order_by(UserPictures.picture_datetime.desc())
                .limit(1)
                .dicts())

        for row in lat:
            last_lat = float(row['location_latitude'])

        # print(last_long, last_lat) 
        # return {
        #     'long': last_long,
        #     'lat': last_lat
        # }
            
        # calculate distances from last-visited picture to each street and take 10 closest streets
        subquery_1 = (Locations
            .select(Locations.street, fn.sqrt(fn.pow(last_lat-Locations.latitude, 2) + 
                                              fn.pow(last_long-Locations.longitude, 2))
                    .alias('dist'), Locations.longitude, Locations.latitude)
            .where(fn.sqrt(fn.pow(last_lat-Locations.latitude, 2) + fn.pow(last_long-Locations.longitude, 2)) > 0.1)
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

api.add_resource(Suggestion, '/suggestions/<string:user_id>')


class AllUserLocations(Resource):
    """
    In this function we return all the active users of the last day. We do the following steps:
    
    1. Take the current time when the function is called (current_time)
    2. Get the datetime of yesterday (current_time_minus_one_day)
    3. Query to get all the users.
    4. Return this as a dataframe.
    """

    def get(self):
        current_time = datetime.now() 
        current_time_minus_one_day = datetime.now() - timedelta(days=1)
        
        
        # Checking for users that logged it between yesterday and now, return a dataframe.
        query = (Users
                .select(Users.id,
                        Users.location_latitude.cast("float"),
                        Users.location_longitude.cast("float"),
                        Users.last_update_datetime.cast("float"))
                .where((Users.last_update_datetime > current_time_minus_one_day) &    
                        (Users.last_update_datetime < current_time))
                .dicts()
                .execute())
        
        # Change query to dataframe 
        query_list_of_dicts = [row for row in query]
    
        return query_list_of_dicts
    
api.add_resource(AllUserLocations, '/all-user-locations/')

class CreateUser(Resource):
    def get(self, user_id):
        try: 
            (Users                                          
                .insert(id = user_id)
                .execute())

            return {'status': 'OK'}
        except:
            return {'status': 'ERROR'}           

api.add_resource(CreateUser, '/create/user/<string:user_id>')

class SaveCurrentLocationOfUser(Resource):
    """
    This function updates the location of the given user. But has two scenarios:
    1. User is known in the database: updates his/her location.
    2. User is not known in the database: inserts a new user_id and his/her location.
    """

    def get(self, user_id, long, lat):
        try:
            (Users
            .update(location_latitude=lat,
                location_longitude=long)
            .where(Users.id == user_id)
            .execute())

            return {'status': 'OK'}

        except:
            return {'status': 'ERROR'}   
        
api.add_resource(SaveCurrentLocationOfUser, '/save-current-location/<string:user_id>/<float:long>/<float:lat>/')


class SaveTakenImage(Resource):
    def get(self, user_id, image_id, long, lat):
        """
        This function inserts data into the user_pictures table.
        
        First it ASSUMES that we already checked if the user is known
        in the database.
        """
        
        # Calculate the current time the function is called.
        current_time = datetime.now() 
        
        # Insert the information in the user_pictures table.
        (UserPictures
        .insert(user_id=user_id,
                image=image_id,
                location_latitude = long,
                location_longitude= lat,
                picture_datetime = current_time)
        .execute() 
        )

        return {'status': 'OK'}

api.add_resource(SaveTakenImage, '/save-taken-image/<string:user_id>/<int:image_id>/<float:long>/<float:lat>/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')