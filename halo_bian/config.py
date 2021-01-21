    #!/usr/bin/env python3

import os
import halo_app
from environs import Env
import json
from halo_app.const import LOC,DEV,TST,PRD

print("== start config")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env = Env()
if 'HALO_STAGE' in os.environ:
    STAGE = os.environ['HALO_STAGE']
else:
    STAGE = LOC
THE_ENV = os.path.join(BASE_DIR, '..', 'env', '.env.'+STAGE)
env.read_env(path=THE_ENV,verbose=True)
print('The .env file has been loaded. path= ' + str(THE_ENV))
print(env.dump())



def get_api_url():
    host = os.environ.get('API_HOST', 'localhost')
    port = 5005 if host == 'localhost' else 80
    return f"http://{host}:{port}"

def get_redis_host_and_port():
    host = os.environ.get('REDIS_HOST', 'localhost')
    port = 63791 if host == 'localhost' else 6379
    return dict(host=host, port=port)

def get_email_host_and_port():
    host = os.environ.get('EMAIL_HOST', 'localhost')
    port = 11025 if host == 'localhost' else 587#fix
    http_port = 18025 if host == 'localhost' else 8025
    return dict(host=host, port=port, http_port=http_port)

class Config(object):

    @classmethod
    def get(cls,key):
        return cls.__dict__[key]

    SERVICING_SESSION = False
    PORT = 8080
    HOST = "127.0.0.1"
    DEBUG = False

    DB_VER = env('DB_VER',None)
    DB_READ_URL = env('DB_READ_URL',None)
    DB_WRITE_URL = env('DB_READ_URL',None)

    SSM_CONFIG = None

    API_PATH = '/loc'
    API_TITLE = 'Advertising'
    API_VERSION = '{}'.format('1.1')
    API_URL_PREFIX = API_PATH+'/api/{}'.format(API_VERSION)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_KEYS = ["1234"]
    INSTANCE_ID = "123"
    ERR_MSG_CLASS = 'halo_app.app.err_msg'


    ONPREM_PROVIDER_CLASS_NAME = "ONPREMProvider"
    ONPREM_PROVIDER_MODULE_NAME = "halo_app.providers.providers"
    ONPREM_SSM_CLASS_NAME = 'OnPremClient'
    ONPREM_SSM_MODULE_NAME = 'halo_app.providers.ssm.onprem_ssm_client'

    FILTER_SEPARATOR = ";"
    SD_REFERENCE_ID_MASK = '^([0-9a-f]+)$'
    CR_REFERENCE_ID_MASK = '^([\s\d]+)$'
    BQ_REFERENCE_ID_MASK = "^([\s\d]+)$"

    REQUEST_FILTER_CONFIG = True

    ###############

    #ENV - flask environment
    #ENV_TYPE - LOC,DEV,TST,PRD
    #ENV_NAME - LOC or HALO_STAGE
    #STAGE_URL - prefix for url

    ENV = env.str('FLASK_ENV', default='production')
    DEBUG = ENV == 'development'
    SQLALCHEMY_DATABASE_URI = env.str('DATABASE_URL')
    SECRET_KEY = env.str('SECRET_KEY')
    BCRYPT_LOG_ROUNDS = env.int('BCRYPT_LOG_ROUNDS', default=13)
    DEBUG_TB_ENABLED = DEBUG
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEBPACK_MANIFEST_PATH = 'webpack/manifest.json'
    WTF_CSRF_CHECK_DEFAULT = False


    ENV_TYPE = LOC

    ENV_NAME = LOC

    APP_NAME = 'halo_current-accountv2' #env var HALO_APP_NAME

    FUNC_NAME='halo_app' #env var HALO_FUNC_NAME


    #@TODO load config view from env var if possible and if not from env file
    SERVER_LOCAL = env.bool('SERVER_LOCAL', default=False)
    PROVIDER = env.str('PROVIDER')
    AWS_REGION = env.str('AWS_REGION')
    DB_URL = env.str('DYNAMODB_URL')
    SECRET_JWT_KEY = env.str('SECRET_JWT_KEY')
    STAGE_URL=env.bool('STAGE_URL',default=True)
    SITE_NAME = env.str('SITE_NAME')

    # SECURITY WARNING: keep the secret key used in production secret!
    # Make this unique, and don't share it with anybody.
    SECRET_KEY = env.str('SECRET_KEY')

    ###
    #Given a version number MAJOR.MINOR.PATCH, increment the:
    #
    #MAJOR version when you make incompatible  changes,
    #MINOR version when you add functionality in a backwards-compatible manner, and
    #PATCH version when you make backwards-compatible bug fixes.
    ###

    title='halo_current-accountv2'
    author='Author'
    copyright='Copyright 2017-2018 '+ author
    major='1'
    minor='1'
    patch='52'
    version=major+'.'+minor+'.'+patch
    #year.month.day.optional_revision  i.e 2016.05.03 for today
    rev=1
    build='2018.10.10.'+str(rev)
    generate='2020.07.26.00:11:48'
    print("generate="+generate)

    def get_version(cls):
        """
        Return package version as listed in  env file
        """
        if Config.ENV_TYPE == PRD:
            return Config.version + "/" + Config.build
        return Config.version + "/" + Config.build + "/" + Config.generate+ ' (' + Config.ENV_NAME + ')'


    #VERSION = cls.get_version()
    #print(VERSION)

    APPEND_SLASH = True

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = env.bool('DEBUG', default=False)
    print("DEBUG="+str(DEBUG))

    SERVER = env.str('SERVER_NAME')
    HALO_HOST = env.str('HALO_HOST',None)

    ADMINS = (
        # ('Your Name', 'your_email@domain.com'),
    )

    MANAGERS = ADMINS

    DB_VER = env.str('DB_VER', default='0')
    PAGE_SIZE = env.int('PAGE_SIZE', default=5)
    def get_db(cls):
        return {
            'default': env.db(),
        }
    #DATABASES = get_db()

    def get_cache(cls):
      return {
          'default': env.cache()
        }
    #CACHES = get_cache()

    # Local time zone for this installation. Choices can be found here:
    # http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
    # although not all choices may be available on all operating systems.
    # On Unix systems, a value of None will cause  to use the same
    # timezone as the operating system.
    # If running in a Windows environment this must be set to the same as your
    # system time zone.
    USE_TZ = True
    TIME_ZONE = 'America/Chicago'

    # Language code for this installation. All choices can be found here:
    # http://www.i18nguy.com/unicode/language-identifiers.html
    LOCALE_CODE = 'en-US'
    LANGUAGE_CODE = 'en'

    LANGUAGES = (
        ('en', str('English')),
        #('nl', _('Dutch')),
        #('he', _('Hebrew')),
    )

    GET_LANGUAGE = True

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'main_formatter': {
                'format': '%(levelname)s:%(name)s: %(message)s '
                          '%(asctime)s; %(filename)s:%(lineno)d',
                'datefmt': "%Y-%m-%d %H:%M:%S",
                'class': "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
            'main_formatter_old': {
                'format': '%(levelname)s:%(name)s: %(message)s '
                          '(%(asctime)s; %(filename)s:%(lineno)d)',
                'datefmt': "%Y-%m-%d %H:%M:%S",
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'main_formatter',
            },
            'console_debug_false': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'main_formatter',
            },
            'mail_admins': {
                'level': 'ERROR',
                'formatter': 'main_formatter',
                'class': 'logging.StreamHandler'
            }
        },
        'loggers': {
            'tester.api.view': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'tester.api.models': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'tester.api.apis': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'tester.api.events': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'tester.handler': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'halo_app.app.viewsx': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'halo_app.apis': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'halo_app.events': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'halo_app.app.mixinx': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'halo_app.models': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'halo_app.app.utilx': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'halo_app.ssm': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'halo_app.saga': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'tester.app.err_msg': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'tester.app.hooks': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
            'tester.app.handler': {
                'level': 'DEBUG',
                'handlers': ['console', 'console_debug_false', 'mail_admins']
            },
        },
    }
    import logging.config
    logging.config.dictConfig(LOGGING)

    USER_HEADERS = 'Mozilla/5.0'

    MIXIN_HANDLER = 'halo_app.app.handler'

    SERVICE_READ_TIMEOUT_IN_SC = 3  # in seconds = 300 ms

    SERVICE_CONNECT_TIMEOUT_IN_SC = 3  # in seconds = 300 ms

    RECOVER_TIMEOUT_IN_SC = 0.5  # in seconds = 500 ms

    MINIMUM_SERVICE_TIMEOUT_IN_SC = 0.1  # in seconds = 100 ms

    HTTP_MAX_RETRY = 4

    THRIFT_MAX_RETRY = 4

    HTTP_RETRY_SLEEP = 10 #0.100  # in seconds = 100 ms

    #in case a web edge
    FRONT_WEB = False #env.str('FRONT_API',default=False)
    file_dirname = os.path.dirname(__file__)
    fr_file_path = os.path.join(file_dirname, "front_web.txt")
    if os.path.exists(fr_file_path):
        FRONT_WEB = True
        # for screen messages

    print ("FRONT_WEB:"+str(FRONT_WEB))

    #in case an api edge
    FRONT_API = False #env.str('FRONT_API',default=False)
    file_dirname = os.path.dirname(__file__)
    fr_file_path = os.path.join(file_dirname, "front_api.txt")
    if os.path.exists(fr_file_path):
        FRONT_API = True
    print ("FRONT_API:"+str(FRONT_API))

    import uuid
    INSTANCE_ID = uuid.uuid4().__str__()[0:4]

    LOG_SAMPLE_RATE = 0.05 # 5%

    SSM_TYPE = env.str('SSM_TYPE',default='NONE')
    print('SSM_TYPE='+SSM_TYPE)

    file_path = os.path.join(BASE_DIR, 'schema', "saga_schema.json")
    with open(file_path) as f1:
        SAGA_SCHEMA = json.load(f1)

    ISOLATION_LEVEL = env.str('ISOLATION_LEVEL',default="REPEATABLE READ")


    ############################################################################################
    HALO_CONTEXT_LIST = []  # ["CORRELATION"]
    HALO_CONTEXT_CLASS = None
    HALO_CLIENT_CLASS = None
    HALO_RESPONSE_FACTORY_CLASS = None
    REQUEST_FILTER_CLASS = None
    REQUEST_FILTER_CLEAR_CLASS = None
    HALO_SECURITY_CLASS = None
    SECURITY_FLAG = False
    SESSION_MINUTES = 30

    API_CONFIG = None
    API_SETTINGS = ENV_NAME + '_api_settings.json'

    file_path = os.path.join(BASE_DIR,'..','env','api', API_SETTINGS)
    if os.path.exists(file_path):
        with open(file_path, 'r') as fi:
            API_CONFIG = json.load(fi)
            print("api_config:" + str(API_CONFIG))
    else:
        print("no api config file")

    BUSINESS_EVENT_MAP = None
    HANDLER_MAP = {}
    EVENT_SETTINGS = ENV_NAME + '_event_settings.json'
    file_path = os.path.join(BASE_DIR,'..','env','config', EVENT_SETTINGS)
    if os.path.exists(file_path):
        with open(file_path, 'r') as fi:
            map = json.load(fi)
            BUSINESS_EVENT_MAP = {}
            for clazz in map:
                bqs = map[clazz]
                dictx = {}
                for bq in bqs:
                    BUSINESS_EVENT_MAP[clazz] = bq
                    val = bqs[bq]
                    dict = {}
                    for action in val:
                        item = val[action]
                        file_path_data = os.path.join(BASE_DIR, '..', 'env', 'config', item['url'])
                        print(file_path_data)
                        with open(file_path_data, 'r') as fx:
                             data = json.load(fx)
                             dict[action] = { item['type'] : data }
                        HANDLER_MAP[action] = {"class": clazz,"type":bq}
                    dictx[bq] = dict
                BUSINESS_EVENT_MAP[clazz] = dictx
    else:
        print("no event config files")


    MAPPING = None
    file_path = os.path.join(BASE_DIR,'..', 'env','config','data_mapping.json')
    try:
        with open(file_path, 'r') as fi:
            MAPPING = json.load(fi)
            print("mapping:" + str(MAPPING))
    except FileNotFoundError as e:
        raise e

    FACTORY_CLASS_LIST = {}
    file_dir = os.path.dirname(__file__)
    for f in os.listdir(file_dir):
        if f.endswith(".json"):
            service_file_name = f.replace(".json","")+"_service"
            file_path = os.path.join(file_dir,f)
            try:
                with open(file_path, 'r') as fi:
                    import ast
                    MAPPING = ast.literal_eval(fi.read())
                    for key in MAPPING:
                        FACTORY_CLASS_LIST[key] = FUNC_NAME+".app.services."+service_file_name+"."+MAPPING[key]
            except FileNotFoundError as e:
                raise e


    host = os.environ.get('DB_HOST', 'localhost')
    port = 54321 if host == 'localhost' else 5432
    password = os.environ.get('DB_PASSWORD', 'abc123')
    user, db_name = 'allocation', 'allocation'
    POSTGRES_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"



print('== The base settings file has been loaded.')


class Config_loc(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    FLASK_ENV = "local"
    HALO_CLIENT_CLASS = 'tests.test_flask.XClientType'
    HALO_RESPONSE_FACTORY_CLASS = 'tests.test_flask.XHaloResponseFactory'

class Config_dev(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    FLASK_ENV = "development"


class Config_tst(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    FLASK_ENV = "development"


class Config_prd(Config):
    PORT = os.getenv("PORT")
    HOST = os.getenv("HOST")
    DEBUG = False
    TESTING = False
    FLASK_DEBUG = False
    FLASK_ENV = "production"

    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI")