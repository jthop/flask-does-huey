# -*- coding: utf-8 -*-
"""

───│─────────────────────────────────────
───│────────▄▄───▄▄───▄▄───▄▄───────│────
───▌────────▒▒───▒▒───▒▒───▒▒───────▌────
───▌──────▄▀█▀█▀█▀█▀█▀█▀█▀█▀█▀▄─────▌────
───▌────▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄───▋────
▀███████████████████████████████████████▄─
──▀██████ flask-does-huey ████████████▀──
─────▀██████████████████████████████▀────
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

CONFIG 

    FLASK_DOES_HUEY_URL or REDIS_URL
    FLASK_DOES_HUEY_HOST or REDIS_HOST
    FLASK_DOES_HUEY_PORT or REDIS_PORT
    FLASK_DOES_HUEY_DB or REDIS_DB
    FLASK_DOES_HUEY_USERNAME or REDIS_USERNAME
    FLASK_DOES_HUEY_PASSWORD or REDIS_PASSWORD

HOW TO

    app = Flask(__name__)
    h = huey_factory.HueyFactory(app)
    huey_instance = h.huey

     -OR-

    h = huey_factory.HueyFactory()
    def create_app():
        app = Flask(__name__)
        h.init_app(app)
    huey_instance = h.huey

"""

from os import environ as env
from huey import RedisHuey


__version__ = '0.5.2'
__author__ = '@jthop'


class HueyFactory(object):
    def __init__(self, app=None, pool=None):
        """
        We can set some variables here but no work until we 
        have an app instance.  This way we support Flask's 
        application factory pattern
        """

        self.__version__ = __version__
        self._initialized = False
        self._config = None
        self._name = None
        self._redis_pool = None
        self.flask_app = None
        self.huey = None

        if app is not None:
            self.init_app(app, pool=pool)
        if pool is not None:
            self._redis_pool = pool

    @property
    def initialized(self):
        """
        Just in case you are curious if the factory is initiated yet
        """

        return self._initialized

    @property
    def is_worker(self):
        """This is useful to instantiate your slimmed flask app instance for
        huey task workers. 
        Required: APP_TASK_WORKER environment variable
        """

        worker = env.get('TASK_WORKER')
        return worker

    def _fetch_config(self):
        """
        Fetch config in the FLASK_DOES_HUEY_ namespace from the app.config dict.
        """

        cfg = self.flask_app.config.get_namespace('FLASK_DOES_HUEY_')
        clean = {k: v for k, v in cfg.items() if v is not None}
        self._config = clean

    def init_app(self, app, pool=None):
        """Delayed instance initiation for application factory pattern
        Args:
            app: Flask app beinging initialized from
            pool(optional): Redis connection pool to use for the redis backend.  
                If not supplied, a normal redis connection will be used.  The 
                pool is useful when you want to reuse the pool for other redis
                connections in your app.
        """

        self.flask_app = app
        self._name = self.flask_app.import_name
        self._redis_pool = pool

        if self._redis_pool is None:
            self._fetch_config()
            url = self._config.get('url')

            # if a url is supplied in config use it, 
            # otherwise hope for enough to connect to redis
            if url:
                self.huey = RedisHuey(self._name, url=url)
            else:
                self.huey = RedisHuey(self._name, **self._config)
        else:
            self.huey = RedisHuey(self._name, connection_pool=pool)

        self._initialized = True
        return
    
