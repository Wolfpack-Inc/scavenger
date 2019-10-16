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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')