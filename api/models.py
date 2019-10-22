from peewee import *

database = MySQLDatabase('scavenger', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': '165.22.199.122', 'user': 'remote', 'password': 'EtrPCEc0jt'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Images(BaseModel):
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
    user_pictures_datetime = DateTimeField()
    user_pictures_image = ForeignKeyField(column_name='user_pictures_image_id', field='id', model=Images)
    user_pictures_location_lat = DecimalField()
    user_pictures_location_long = DecimalField()
    user_pictures_user = ForeignKeyField(column_name='user_pictures_user_id', field='id', model=Users)

    class Meta:
        table_name = 'user_pictures'
        indexes = (
            (('user_pictures_user', 'user_pictures_location_lat', 'user_pictures_location_long', 'user_pictures_image', 'user_pictures_datetime'), True),
        )
        primary_key = CompositeKey('user_pictures_datetime', 'user_pictures_image', 'user_pictures_location_lat', 'user_pictures_location_long', 'user_pictures_user')

