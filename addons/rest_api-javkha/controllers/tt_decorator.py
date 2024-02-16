import inspect
import logging

import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers

try:
    from werkzeug.middleware.shared_data import SharedDataMiddleware
except ImportError:
    from werkzeug.wsgi import SharedDataMiddleware

try:
    import psutil
except ImportError:
    psutil = None

_logger = logging.getLogger(__name__)

import functools

import werkzeug.wrappers

from odoo.http import request, Response
from .tt_plugin_functions import (error_response)

try:
    import simplejson as json
except ImportError:
    import json

####################################
# Definition of global error codes #
####################################

# 2xx Success
RETURN_CODE__success = 200
RETURN_CODE__created = 201
RETURN_CODE__accepted = 202
RETURN_CODE__ok_no_content = 204

# 4xx Client Errors
RETURN_CODE__server_rejects = (400, "Server rejected", "Welcome to Tortecs!")
RETURN_CODE__no_user_auth = (401, "Authentication", "Your token could not be authenticated.")
RETURN_CODE__user_no_perm = (403, "Permissions", "%s")
RETURN_CODE__method_blocked = (403, "Blocked Method", "This method is not whitelisted on this model.")
RETURN_CODE__db_not_found = (404, "Db not found", "Welcome to macondo!")
RETURN_CODE__canned_ctx_not_found = (404, "Canned context not found",
                                     "The requested canned context is not configured on this model")
RETURN_CODE__obj_not_found = (404, "Object not found", "This object is not available on this instance.")
RETURN_CODE__res_not_found = (404, "Resource not found", "There is no resource with this id.")
RETURN_CODE__act_not_executed = (409, "Action not executed", "The requested action was not executed.")

# 5xx Server errors
RETURN_CODE__invalid_method = (501, "Invalid Method", "This method is not implemented.")
RETURN_CODE__invalid_spec = (501, "Invalid Field Spec", "The field spec supplied is not valid.")

# If API Workers are enforced, but non is available (switched off)
RETURN_CODE__no_api_worker = (503, "API worker sleeping", "The API worker is currently not at work.")


##########################
# REST API Authentication #
##########################


def get_auth_header(headers, raise_exception=False):
    """check and get basic authentication header from headers

    :param werkzeug.datastructures.Headers headers: All headers in request.
    :param bool raise_exception: raise exception.

    :returns: Found raw authentication header.`
    :rtype: str or None

    :raise: werkzeug.exceptions.HTTPException if raise_exception is **True**
                                              and auth header is not in headers
                                              or it is not Basic type.
    """
    raw_data = request.httprequest.data
    # body = json.loads(raw_data)
    auth_header = headers.get('Access-Token') or headers.get('access-token') or headers.get('Access-token') or headers.get('Authorization')
    if not auth_header:
        if raise_exception:
            raise werkzeug.exceptions.HTTPException(
                response=error_response(*RETURN_CODE__no_user_auth)
            )
    return auth_header


def validate_access_token(token):
    """
    :param str token: The API token.

    :returns: a tuple of database name and user token
    :rtype: tuple
    :raise: werkzeug.exceptions.HTTPException if basic header is invalid base64
                                              string or if the basic header is
                                              in the wrong format
    """
    token_id = request.env['tortecs.rest.api'].sudo().search([('tt_api_token', '=', token)])
    print(token_id,'-------------++++++++++++++++++++-------------')
    if token_id.tt_is_expired:
        raise werkzeug.exceptions.HTTPException(
            response=error_response(
                500, "Invalid token", "API Token either missing or invalid.\nPlease contact your Administrator"
            )
        )
    elif not token_id:
        return False
    else:
        if token_id.tt_access == 'specific':
            pass
        else:
            return True


# patch http.route to authenticate access token
def route(route=None, **kw):
    routing = kw.copy()
    assert 'type' not in routing or routing['type'] in ("http", "json")

    def decorator(f):
        if route:
            if isinstance(route, list):
                routes = route
            else:
                routes = [route]
            routing['routes'] = routes

        @functools.wraps(f)
        def response_wrap(*args, **kw):
            # if controller cannot be called with extra args (utm, debug, ...), call endpoint ignoring them
            params = inspect.signature(f).parameters.values()
            auth_header = get_auth_header(
                request.httprequest.headers, raise_exception=True
            )
            result = validate_access_token(auth_header)
            print(result,'-result--------------------')
            if not result:
                raise werkzeug.exceptions.HTTPException(
                    response=error_response(
                        500, "Invalid token", "API Token either missing or invalid.\nPlease contact your Administrator"
                    )
                )
            is_kwargs = lambda p: p.kind == inspect.Parameter.VAR_KEYWORD
            if not any(is_kwargs(p) for p in params):  # missing **kw
                is_keyword_compatible = lambda p: p.kind in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY)
                fargs = {p.name for p in params if is_keyword_compatible(p)}
                ignored = ['<%s=%s>' % (k, kw.pop(k)) for k in list(kw) if k not in fargs]
                if ignored:
                    _logger.info(
                        "<function %s.%s> called ignoring args %s" % (f.__module__, f.__name__, ', '.join(ignored)))

            response = f(*args, **kw)

            if isinstance(response, Response) or f.routing_type == 'json':
                print(response,'-=')
                return response

            if isinstance(response, (bytes, str)):
                print(response,'=====')
                return Response(response)

            if isinstance(response, werkzeug.exceptions.HTTPException):
                response = response.get_response(request.httprequest.environ)
            if isinstance(response, werkzeug.wrappers.BaseResponse):
                response = Response.force_type(response)
                response.set_default()
                print(response,'----')
                return response
            _logger.warning(
                "<function %s.%s> returns an invalid response type for an http request" % (f.__module__, f.__name__))
            return response

        response_wrap.routing = routing
        response_wrap.original_func = f
        return response_wrap
    return decorator
