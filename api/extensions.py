from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_compress import Compress

from db import Base, Base2

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
db = SQLAlchemy(model_class=Base)
db2 = SQLAlchemy(model_class=Base2)
compress = Compress()
