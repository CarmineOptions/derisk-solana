from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_compress import Compress

from db import Base

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
db = SQLAlchemy(model_class=Base)
compress = Compress()
