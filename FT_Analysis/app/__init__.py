from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
cache.init_app(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#if __name__ == '__main__':
    #app.run()


from app import routes, models
#app.run(host="0.0.0.0", port=8000)
