# encoding: utf-8
import http
import requests

from ..config import CxConfig
from ..exceptions.CxError import BadRequestError, CxError
from .dto import (CxAuthRequest, CxAuthResponse)


class AuthenticationAPI(object):
    """
    Token-based Authentication
    """
    token_url = CxConfig.CxConfig.config.config.url + "/auth/identity/connect/token"
    auth_headers = None

    def __init__(self):
        """

        """
        self.reset_auth_headers()

    @classmethod
    def reset_auth_headers(cls):
        """
        use the credentials from config.ini to get access token, store it in a CxAuthResponse object,
        get the HTTP header

        Returns:
            dict
                the HTTP header that will be used in other REST API
        """
        config_info = CxConfig.CxConfig.config
        req_data = CxAuthRequest.CxAuthRequest(
            username=config_info.username, password=config_info.password,
            grant_type=config_info.grant_type, scope=config_info.scope,
            client_id=config_info.client_id, client_secret=config_info.client_secret
        ).get_post_data()
        r = requests.post(url=AuthenticationAPI.token_url, data=req_data)
        if r.status_code == http.HTTPStatus.OK:
            d = r.json()
            auth_response = CxAuthResponse.CxAuthResponse(
                d.get("access_token"), d.get("expires_in"), d.get("token_type")
            )
            AuthenticationAPI.auth_headers = {
                "Authorization": auth_response.token_type + " " + auth_response.access_token,
                "Accept": "application/json;v=1.0",
                "Content-Type": "application/json;v=1.0",
                "cxOrigin": "REST API"
            }
        elif r.status_code == http.HTTPStatus.BAD_REQUEST:
            raise BadRequestError(r.text)
        else:
            raise CxError(r.text, r.status_code)

        return AuthenticationAPI.auth_headers


AuthenticationAPI()
