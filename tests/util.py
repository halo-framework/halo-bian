
import logging
from http import HTTPStatus
from halo_app.app.context import HaloContext
from halo_app.app.exceptions import HttpFailException
from halo_app.classes import AbsBaseClass
from halo_app.entrypoints.client_type import ClientType
from halo_app.logs import log_json

from halo_app.settingsx import settingsx
settings = settingsx()

logger = logging.getLogger(__name__)

class Util(AbsBaseClass):

    @classmethod
    def process_api_ok(cls, halo_response,method):
        if halo_response:
            if halo_response.request.context.get(HaloContext.client_type) == ClientType.api:
                if halo_response.success:
                    if settings.ASYNC_MODE:
                        success = HTTPStatus.ACCEPTED
                    else:
                        success = HTTPStatus.OK
                    if halo_response.request:
                        if halo_response.request.context:
                            halo_response.code = success
                            if method == 'GET':
                                halo_response.code = success
                            if method == 'POST':
                                if success == HTTPStatus.ACCEPTED:
                                    halo_response.code = HTTPStatus.ACCEPTED
                                else:
                                    halo_response.code = HTTPStatus.CREATED
                            if method == 'PUT':
                                halo_response.code = HTTPStatus.ACCEPTED
                            if method == 'PATCH':
                                halo_response.code = HTTPStatus.ACCEPTED
                            if method == 'DELETE':
                                halo_response.code = success
                            logger.info('process_service_operation : '+halo_response.request.method_id,
                                        extra=log_json(halo_response.request.context,  {"return": "success"}))
                            return halo_response
                else:
                    halo_response.code = HTTPStatus.INTERNAL_SERVER_ERROR
                    if halo_response.errors: # invalid params
                        halo_response.code = HTTPStatus.BAD_REQUEST
                    halo_response.payload = halo_response.errors
                    return halo_response
        raise HttpFailException(halo_response)