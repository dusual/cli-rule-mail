import os
from datetime import datetime

from pony.orm import *

db = Database()
sql_debug(True)
if not os.path.exists:
    db.bind('sqlite', './maildb.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)

class Message(db.Entity):
    id = PrimaryKey(int, auto=True)
    gmail_id = Required(str)
    from_email = Required(str)
    to_email = Required(str)
    subject = Required(str)
    date = Required(datetime)















db.bind(provider='sqlite', filename='./mails.sqlite', create_db=True)
db.generate_mapping(create_tables=True)