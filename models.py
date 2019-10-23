from peewee import *

database = MySQLDatabase('masterclass', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': '165.22.199.122', 'user': 'remote', 'password': 'EtrPCEc0jt'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Bananas(BaseModel):
    color = CharField(null=True)
    idbananas = AutoField()
    length = IntegerField(null=True)

    class Meta:
        table_name = 'bananas'

