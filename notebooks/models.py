from peewee import *

database = MySQLDatabase('scavenger', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': '165.22.199.122', 'user': 'remote', 'password': 'EtrPCEc0jt'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Images(BaseModel):
    points = IntegerField(null=True)
    street = TextField(null=True)
    title = TextField(null=True)
    url = TextField(null=True)
    usable = IntegerField(null=True)
    year = IntegerField(null=True)

    class Meta:
        table_name = 'images'

class Locations(BaseModel):
    index = BigAutoField()
    latitude = FloatField()
    longitude = FloatField()
    map_avg_lat = FloatField(null=True)
    map_avg_long = FloatField(null=True)
    map_bot_lat = FloatField(null=True)
    map_bot_long = FloatField(null=True)
    map_top_lat = FloatField(null=True)
    map_top_long = FloatField(null=True)
    radius = FloatField(null=True)
    street = CharField()

    class Meta:
        table_name = 'locations'

class Users(BaseModel):
    current_image_id = IntegerField(null=True)
    last_update_datetime = DateTimeField(null=True)
    location_latitude = DecimalField()
    location_longitude = DecimalField()
    profile_picture = CharField(null=True)

    class Meta:
        table_name = 'users'

class UserPictures(BaseModel):
    image = ForeignKeyField(column_name='image_id', field='id', model=Images)
    location_latitude = DecimalField()
    location_longitude = DecimalField()
    picture_datetime = DateTimeField()
    user = ForeignKeyField(column_name='user_id', field='id', model=Users)

    class Meta:
        table_name = 'user_pictures'
        indexes = (
            (('user', 'location_latitude', 'location_longitude', 'image', 'picture_datetime'), True),
        )
        primary_key = CompositeKey('image', 'location_latitude', 'location_longitude', 'picture_datetime', 'user')

