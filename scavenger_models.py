from peewee import *

database = MySQLDatabase('scavenger', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': '165.22.199.122', 'user': 'remote', 'password': 'EtrPCEc0jt'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Images(BaseModel):
    index = BigIntegerField(index=True, null=True)
    street = TextField(null=True)
    title = TextField(null=True)
    url = TextField(null=True)
    year = TextField(null=True)

    class Meta:
        table_name = 'images'
        primary_key = False

class Locations(BaseModel):
    dis_lat = FloatField(null=True)
    dis_long = FloatField(null=True)
    index = BigIntegerField(index=True, null=True)
    map_avg_lat = FloatField(null=True)
    map_avg_long = FloatField(null=True)
    map_bot_lat = FloatField(null=True)
    map_bot_long = FloatField(null=True)
    map_top_lat = FloatField(null=True)
    map_top_long = FloatField(null=True)
    nav_lat = FloatField(null=True)
    nav_long = FloatField(null=True)
    street = CharField(primary_key=True)

    class Meta:
        table_name = 'locations'

