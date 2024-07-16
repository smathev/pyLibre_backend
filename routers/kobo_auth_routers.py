from binascii import hexlify
from datetime import datetime
from os import urandom
from functools import wraps
from fastapi.responses import JSONResponse

from schemas.response_models import (BaseResponse, 
                                     AuthTokenData)


from fastapi import APIRouter, HTTPException, Request

from db.kobo_auth_models import KoboAuthManager

from loguru import logger

router = APIRouter()

@router.post("/kobo/generate_auth_token/{user_id}", response_model=BaseResponse, tags=["Kobo"])
#@login_required
async def generate_auth_token(user_id, request: Request):
    kobo_auth_processor = KoboAuthManager()    
    warning = False
    # host_list = request.client.host.split(':')  # Extract host information
    # host_list = 'test'
    # if len(host_list) == 1:
    #     host = ':'.join(host_list)
    # else:
    #     host = ':'.join(host_list[0:-1])
    # if host.startswith('127.') or host.lower() == 'localhost' or host.startswith('[::ffff:7f') or host == "[::1]":
    #     warning = ('Please access Calibre-Web from non localhost to get valid api_endpoint for kobo device')
    new_auth_token = await kobo_auth_processor.generate_auth_token(user_id)
    response = BaseResponse(
        status="OK",
        message="New token generated successfully.",
        data=AuthTokenData(auth_token=new_auth_token)
    )
    return JSONResponse(content=response.dict())


@router.delete("/kobo/delete_auth_token/{user_id}", response_model=BaseResponse, tags=["Kobo"])
#@login_required
def delete_auth_token(user_id):
    kobo_auth_processor = KoboAuthManager()
    result = kobo_auth_processor.delete_auth_token(user_id)
    response = BaseResponse(
        status="OK",
        message=result,
        data=None
    )
    return JSONResponse(content=response.dict())

@router.get("/kobo/get_auth_token/{user_id}", response_model=BaseResponse, tags=["Kobo"])
#@login_required
def get_auth_token(user_id: str):
    kobo_auth_processor = KoboAuthManager()
    auth_token = kobo_auth_processor.get_auth_token(user_id)

    if auth_token is not None:
        data = AuthTokenData(auth_token=auth_token)
        response = BaseResponse(
            status="OK",
            message=None,
            data=data
        )
    else:
        response = BaseResponse(
            status="NOT_FOUND",
            message="No auth token found for the given user ID.",
            data=None
        )

    return JSONResponse(content=response.dict())

# def disable_failed_auth_redirect_for_blueprint(bp):
#     lm.blueprint_login_views[bp.name] = None


# def get_auth_token():
#     if "auth_token" in g:
#         return g.get("auth_token")
#     else:
#         return None


# def register_url_value_preprocessor(kobo):
#     @kobo.url_value_preprocessor
#     # pylint: disable=unused-variable
#     def pop_auth_token(__, values):
#         g.auth_token = values.pop("auth_token")


# def requires_kobo_auth(f):
#     @wraps(f)
#     def inner(*args, **kwargs):
#         auth_token = get_auth_token()
#         if auth_token is not None:
#             try:
#                 limiter.check()
#             except RateLimitExceeded:
#                 return abort(429)
#             except (ConnectionError, Exception) as e:
#                 log.error("Connection error to limiter backend: %s", e)
#                 return abort(429)
#             user = (
#                 ub.session.query(ub.User)
#                 .join(ub.RemoteAuthToken)
#                 .filter(ub.RemoteAuthToken.auth_token == auth_token).filter(ub.RemoteAuthToken.token_type==1)
#                 .first()
#             )
#             if user is not None:
#                 login_user(user)
#                 [limiter.limiter.storage.clear(k.key) for k in limiter.current_limits]
#                 return f(*args, **kwargs)
#         log.debug("Received Kobo request without a recognizable auth token.")
#         return abort(401)
#     return inner