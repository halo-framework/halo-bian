# Django settings for checkerservice project.


import json
import os
from environs import Env
from halo_flask.const import LOC,DEV,TST,PRD

print("start base")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = Env()
THE_ENV=os.path.join(BASE_DIR,'env','.env')
env.read_env(path=THE_ENV)

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


ENV_NAME = LOC

ENV_TYPE = LOC

FUNC_NAME = 'sdapi'
APP_NAME = 'sdapp'

SERVER_LOCAL = env.bool('SERVER_LOCAL', default=False)
DB_URL = env.str('DYNAMODB_URL')
SECRET_JWT_KEY = env.str('SECRET_JWT_KEY')
STAGE_URL = env.bool('STAGE_URL', default=True)
SITE_NAME = env.str('SITE_NAME')

# SECURITY WARNING: keep the secret key used in production secret!
# Make this unique, and don't share it with anybody.
SECRET_KEY = env.str('SECRET_KEY')

###
# Given a version number MAJOR.MINOR.PATCH, increment the:
#
# MAJOR version when you make incompatible  changes,
# MINOR version when you add functionality in a backwards-compatible manner, and
# PATCH version when you make backwards-compatible bug fixes.
###

title = 'sdapi'
author = 'Author'
copyright = 'Copyright 2017-2018 ' + author
major = '1'
minor = '1'
patch = '52'
version = major + '.' + minor + '.' + patch
# year.month.day.optional_revision  i.e 2016.05.03 for today
rev = 1
build = '2018.10.10.' + str(rev)
generate = '2019.01.01.02:05:05'
print("generate=" + generate)


def get_version():
    """
    Return package version as listed in  env file
    """
    if ENV_TYPE == PRD:
        return version + "/" + build
    return version + "/" + build + "/" + generate + ' (' + ENV_NAME + ')'


VERSION = get_version()
print(VERSION)

APPEND_SLASH = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)
print("DEBUG=" + str(DEBUG))

SERVER = env.str('SERVER_NAME')
HALO_HOST = 'halo_bian'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DB_VER = env.str('DB_VER', default='0')
PAGE_SIZE = env.int('PAGE_SIZE', default=5)


# DATABASES = {
#    'default': env.db(),
# }

def get_cache():
    return {
        'default': env.cache()
    }


# CACHES = get_cache()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
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
    # ('nl', _('Dutch')),
    # ('he', _('Hebrew')),
)

GET_LANGUAGE = True

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, '../locale'),
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'


CORS_ORIGIN_ALLOW_ALL = True

# STATIC_URL = '/static/'
STATIC_URL = "/" + ENV_NAME + '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "api/static")

STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, "api/static"),
    # '/var/www/static/',
]

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
        #    'file': {
        #        'level': 'DEBUG',
        #        'class': 'logging.FileHandler',
        #        'filename': '/path/to/django/debug.log',
        #    },
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
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'mail_admins': {
            'level': 'ERROR',
            'formatter': 'main_formatter',
            'class': 'logging.StreamHandler'  # 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'sdapiservice.api.views': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'sdapiservice.api.models': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'sdapiservice.api.apis': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'sdapiservice.api.events': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'sdapiservice.handler': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.views': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.apis': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.circuitbreaker': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.events': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.mixin': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.models': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.util': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.ssm': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'halo_flask.saga': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'sdapiservice.api.mixin.mixin_view': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'sdapiservice.api.mixin.mixin_db': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
        'sdapiservice.api.mixin.mixin_handler': {
            'level': 'DEBUG',
            'handlers': ['console', 'console_debug_false', 'mail_admins']
        },
    },
}
import logging.config

logging.config.dictConfig(LOGGING)

USER_HEADERS = 'Mozilla/5.0'

MIXIN_HANDLER = 'sdapiservice.api.mixin.mixin_handler'

SERVICE_READ_TIMEOUT_IN_MS = 3  # in seconds

SERVICE_CONNECT_TIMEOUT_IN_MS = 3  # in seconds

HTTP_MAX_RETRY = 4

THRIFT_MAX_RETRY = 4

HTTP_RETRY_SLEEP = 0.300  # in seconds

ERR_MSG_CLASS = 'sdapiservice.api.mixin.mixin_err_msg'

# in case a web edge
FRONT_WEB = False  # env.str('FRONT_API',default=False)
file_dirname = os.path.dirname(__file__)
fr_file_path = os.path.join(file_dirname, "front_web.txt")
if os.path.exists(fr_file_path):
    FRONT_WEB = True
    # for screen messages

print("FRONT_WEB:" + str(FRONT_WEB))

# in case an api edge
FRONT_API = False  # env.str('FRONT_API',default=False)
file_dirname = os.path.dirname(__file__)
fr_file_path = os.path.join(file_dirname, "front_api.txt")
if os.path.exists(fr_file_path):
    FRONT_API = True
print("FRONT_API:" + str(FRONT_API))

import uuid

INSTANCE_ID = uuid.uuid4().__str__()[0:4]

LOG_SAMPLE_RATE = 0.05  # 5%

############################################################################################


API_CONFIG = None
API_SETTINGS = ENV_NAME + '_api_settings.json'

file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir,'env','api', API_SETTINGS)
with open(file_path, 'r') as fi:
    API_CONFIG = json.load(fi)
    print("api_config:" + str(API_CONFIG))

file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir,'env', 'loc_settings.json')
with open(file_path, 'r') as fi:
    LOC_TABLE = json.load(fi)
    print("loc_settings:" + str(LOC_TABLE))

"""
API_CONFIG = {}
API_SETTINGS = ENV_NAME + '_api_settings.json'
file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir, API_SETTINGS)
if os.path.exists(file_path):
    with open(file_path, 'r') as fi:
        API_CONFIG = json.load(fi)
        print("api_config:" + str(API_CONFIG))
else:
    print("no api config file")

SSM_CONFIG = None
print("get config from ssm")
try:
    from halo_flask.ssm import get_config, set_param_config

    SSM_CONFIG = get_config(AWS_REGION)
except Exception as e:
    print("error loading ssm:" + str(e))

SSM_APP_CONFIG = None
print("get app config from ssm")
try:
    from halo_flask.ssm import get_app_config, set_app_param_config

    SSM_APP_CONFIG = get_app_config(AWS_REGION)

    for item in SSM_APP_CONFIG.cache.items:
        if item not in [FUNC_NAME, 'DEFAULT']:
            url = SSM_APP_CONFIG.get_param(item)["url"]
            print(item + ":" + url)
            for key in API_CONFIG:
                current = API_CONFIG[key]
                new_url = current["url"]
                if "service://" + item in new_url:
                    API_CONFIG[key]["url"] = new_url.replace("service://" + item, url)
    print(str(API_CONFIG))
except Exception as e:
    print("error loading app ssm:" + str(e))
"""


#extend sample

from halo_bian.bian.bian import FunctionalPatterns
BIAN_VER = "8"
BIAN_API_VER = "2.0"
HALO_CONTEXT_LIST = []
HALO_CONTEXT_CLASS = 'tests.tests_bian.CAContext'
REQUEST_FILTER_CLASS = 'halo_bian.bian.bian.BianRequestFilter'
REQUEST_FILTER_CLEAR_CLASS = None
CIRCUIT_BREAKER = True
SERVICE_DOMAIN = "halo_current_account_service"
ASSET_TYPE = "currentaccount"
FUNCTIONAL_PATTERN = FunctionalPatterns.FULFILL
GENERIC_ARTIFACT = 'halo_bian.bian.bian.FulfillmentArrangement'#extended classes of FulfillmentArrangement
BEHAVIOR_QUALIFIER_TYPE = 'tests.tests_bian.CAFeature'
BEHAVIOR_QUALIFIER = {
  "Interest":"Interest",
  "ServiceFees":"ServiceFees",
  "AccountLien":"AccountLien",
  "AccountSweep":"AccountSweep",
  "DepositsandWithdrawals":"DepositsandWithdrawals",
  "Payments":"Payments",
  "IssuedDevice":"IssuedDevice"
}
SUB_QUALIFIER = {
  "DepositsandWithdrawals":{
      "Deposits":{
          "name":"Deposits",
           "subs":{
                "Depositsy":{
                    "name":"Depositsy",
                    "subs":{
                    }
                },
                "Depositsz":{
                    "name":"Depositsz",
                    "subs":{
                    }
                }
            }
        },
      "Withdrawals":{"name":"Withdrawals","subs":{}},
      "Payments":{"name":"Payments","subs":{}}
  },
  "IssuedDevice":{
      "Depositsx":{"name":"Depositsx","subs":{}},
      "Withdrawalsx":{"name":"Withdrawalsx","subs":{}},
      "Paymentsx":{"name":"Paymentsx","subs":{}}
  },
  "ServiceFees":{
      "Depositsk":{"name":"Depositsk","subs":{}},
      "Withdrawalsk":{"name":"Withdrawalsk","subs":{}},
      "Paymentsk":{"name":"Paymentsk","subs":{}}
  }
}
CONTROL_RECORD = 'tests.tests_bian.CAControlRecord'#extended classes of ControlRecord
DBACCESS_CLASS = "halo_bian.bian.db.AbsBianDbMixin"

PROVIDER = 'AWS'
AWS_REGION = 'us-east-1'

FILTER_SEPARATOR = "@"
SD_REFERENCE_ID_MASK = '^([\s\d]+)$'
CR_REFERENCE_ID_MASK = '^([\s\d]+)$'#'././.{4} .{2}:.{2}'#"[0-9]{1,5}"#None
BQ_REFERENCE_ID_MASK = "^([\s\d]+)$"#None

file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir, 'env','config',"saga_schema.json")
with open(file_path) as f1:
    SAGA_SCHEMA = json.load(f1)

BUSINESS_EVENT_MAP = None
EVENT_SETTINGS = ENV_NAME + '_event_settings.json'
file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir,'env','config', EVENT_SETTINGS)
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
                file_path_data = os.path.join(file_dir,'env','config', item['url'])
                print(file_path_data)
                with open(file_path_data, 'r') as fx:
                     data = json.load(fx)
                     dict[action] = { item['type'] : data }
            dictx[bq] = dict
        BUSINESS_EVENT_MAP[clazz] = dictx


MAPPING = None
file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir, 'env','config','mapping.json')
try:
    with open(file_path, 'r') as fi:
        MAPPING = json.load(fi)
        print("mapping:" + str(MAPPING))
except FileNotFoundError as e:
    pass


SERVICE_DOMAINS = None
file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir,'env','config', 'bian_sds.json')
with open(file_path, 'r') as fb:
    SERVICE_DOMAINS = json.load(fb)

SSM_TYPE="AWS"
SERVICE_INFO_CLASS='halo_bian.bian.bian.TheBianServiceInfo'

print('The base settings file has been loaded. bian')