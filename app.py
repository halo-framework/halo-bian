# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask import Flask
from flask_restful import Api
from flask import Flask, render_template
from flask_restful import reqparse, abort, Api, Resource
from halo_flask.ssm import set_app_param_config,set_host_param_config,get_app_param_config
from halo_flask.apis import load_api_config
from halo_flask.flask.viewsx import load_global_data
from halo_flask.base_util import BaseUtil
from halo_bian.bian.abs_bian_srv import AbsBianSrvMixin

def create_app(config_object='settings'):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])

    app.config.from_object(config_object)
    with app.app_context():
        from halo_flask.flask.viewsx import PerfLinkX,HealthLinkX,InfoLinkX#,TestLinkX
        #app.add_url_rule("/", view_func=TestLinkX.as_view("member"))
        app.add_url_rule("/perf", view_func=PerfLinkX.as_view("perf"))
        app.add_url_rule("/info", view_func=InfoLinkX.as_view("info"))
        app.add_url_rule("/health", view_func=HealthLinkX.as_view("health"))
    api = Api(app, catch_all_404s=True)
    register_halo(app)

    return app

def register_halo(app):
    with app.app_context():
        from halo_flask.apis import load_api_config
        if 'SSM_TYPE' in app.config and app.config['SSM_TYPE'] != 'NONE':
            load_api_config(app.config['ENV_TYPE'], app.config['SSM_TYPE'], app.config['FUNC_NAME'],
                            app.config['API_CONFIG'])
            HALO_HOST = BaseUtil.get_host_name()
            params = {}
            params["url"] = set_host_param_config(HALO_HOST)
            set_app_param_config(app.config['SSM_TYPE'], params)
        if 'INIT_DATA_MAP' in app.config and 'INIT_CLASS_NAME' in app.config:
            data_map = app.config['INIT_DATA_MAP']
            class_name = app.config['INIT_CLASS_NAME']
            load_global_data(class_name, data_map)

app = create_app()

# from halolib.halolib.viewsx import TestLinkX, PerfLinkX
# app.add_url_rule("/", view_func=TestLinkX.as_view("member"))
# app.add_url_rule("/perf", view_func=PerfLinkX.as_view("member"))
