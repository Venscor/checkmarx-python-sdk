# encoding: utf-8

import requests
import http


from src.CxRestAPISDK.config import CxConfig
from src.CxRestAPISDK.auth import AuthenticationAPI

from src.CxRestAPISDK.sast.engines.dto import CxRegisterEngineRequestBody, CxEngineServer, CxEngineConfiguration

from src.CxRestAPISDK.sast.projects.dto import CxLink


class EnginesAPI(object):
    """
    engines API
    """
    base_url = CxConfig.CxConfig.config.url
    engine_servers_url = base_url + "/sast/engineServers"
    engine_server_url = base_url + "/sast/engineServers/{id}"
    engine_configurations_url = base_url + "/sast/engineConfigurations"
    engine_configuration_url = base_url + "/sast/engineConfigurations/{id}"

    def __init__(self):
        self.retry = 0

    def get_all_engine_server_details(self):
        """

        :return:
            list of CxEngineServer
        """
        all_engine_server_details = None
        r = requests.get(url=self.engine_servers_url,
                         headers=AuthenticationAPI.AuthenticationAPI.auth_headers)
        if r.status_code == 200:
            a_list = r.json()
            all_engine_server_details = [
                CxEngineServer.CxEngineServer(
                    id=item.get("id"),
                    name=item.get("name"),
                    uri=item.get("uri"),
                    min_loc=item.get("minLoc"),
                    max_loc=item.get("maxLoc"),
                    max_scans=item.get("maxScans"),
                    cx_version=item.get("cxVersion"),
                    status=CxEngineServer.CxEngineServer.Status(
                        id=(item.get("status", {}) or {}).get("id"),
                        value=(item.get("status", {}) or {}).get("value"),
                    ),
                    link=CxLink.CxLink(
                        rel=(item.get("link", {}) or {}).get("rel"),
                        uri=(item.get("link", {}) or {}).get("uri")
                    )
                ) for item in a_list
            ]
        elif r.status_code == http.HTTPStatus.BAD_REQUEST:
            raise Exception("Bad Request")
        elif (r.status_code == http.HTTPStatus.UNAUTHORIZED) and (self.retry < 3):
            AuthenticationAPI.AuthenticationAPI.reset_auth_headers()
            self.retry += 1
            self.get_all_engine_server_details()
        else:
            raise Exception("Network Error")
        return all_engine_server_details

    def register_engine(self, name, uri, min_loc, max_loc, is_blocked):
        """

        :param name:
        :param uri:
        :param min_loc:
        :param max_loc:
        :param is_blocked:
        :return:
        """
        engine_server = None
        post_request_body = CxRegisterEngineRequestBody.CxRegisterEngineRequestBody(
            name=name,
            uri=uri,
            min_loc=min_loc,
            max_loc=max_loc,
            is_blocked=is_blocked
        ).get_post_data()

        r = requests.post(self.engine_servers_url, data=post_request_body,
                          headers=AuthenticationAPI.AuthenticationAPI.auth_headers)

        if r.status_code == 200:
            a_dict = r.json()
            engine_server = CxEngineServer.CxEngineServer(
                id=a_dict.get("id"),
                link=CxLink.CxLink(
                    rel=(a_dict.get("link", {}) or {}).get("rel"),
                    uri=(a_dict.get("link", {}) or {}).get("uri")
                )
            )
        elif r.status_code == http.HTTPStatus.BAD_REQUEST:
            raise Exception("Bad Request")
        elif (r.status_code == http.HTTPStatus.UNAUTHORIZED) and (self.retry < 3):
            AuthenticationAPI.AuthenticationAPI.reset_auth_headers()
            self.retry += 1
            self.register_engine(name, uri, min_loc, max_loc, is_blocked)
        else:
            raise Exception("Network Error")
        return engine_server

    def unregister_engine_by_engine_id(self, engine_id):
        """
        Unregister an existing engine server.
        :param engine_id:
        :return:
        """
        is_successful = False
        self.engine_server_url = self.engine_server_url.format(id=engine_id)
        r = requests.delete(url=self.engine_server_url, headers=AuthenticationAPI.AuthenticationAPI.auth_headers)
        if r.status_code == 204:
            is_successful = True
        elif r.status_code == http.HTTPStatus.BAD_REQUEST:
            raise Exception("Bad Request")
        elif r.status_code == http.HTTPStatus.NOT_FOUND:
            raise Exception("Not Found")
        elif (r.status_code == http.HTTPStatus.UNAUTHORIZED) and (self.retry < 3):
            AuthenticationAPI.AuthenticationAPI.reset_auth_headers()
            self.retry += 1
            self.unregister_engine_by_engine_id(engine_id)
        else:
            raise Exception("Network Error")
        return is_successful

    def get_engine_details(self, engine_id):
        """
        Get details of a specific engine server by Id.
        :param engine_id: int
        :return:
        """
        engine_server = None

        self.engine_server_url = self.engine_server_url.format(id=engine_id)
        r = requests.get(url=self.engine_server_url, headers=AuthenticationAPI.AuthenticationAPI.auth_headers)
        if r.status_code == 200:
            item = r.json()
            engine_server = CxEngineServer.CxEngineServer(
                    id=item.get("id"),
                    name=item.get("name"),
                    uri=item.get("uri"),
                    min_loc=item.get("minLoc"),
                    max_loc=item.get("maxLoc"),
                    max_scans=item.get("maxScans"),
                    cx_version=item.get("cxVersion"),
                    status=CxEngineServer.CxEngineServer.Status(
                        id=(item.get("status", {}) or {}).get("id"),
                        value=(item.get("status", {}) or {}).get("value"),
                    ),
                    link=CxLink.CxLink(
                        rel=(item.get("link", {}) or {}).get("rel"),
                        uri=(item.get("link", {}) or {}).get("uri")
                    )
                )
        elif r.status_code == http.HTTPStatus.BAD_REQUEST:
            raise Exception("Bad Request")
        elif (r.status_code == http.HTTPStatus.UNAUTHORIZED) and (self.retry < 3):
            AuthenticationAPI.AuthenticationAPI.reset_auth_headers()
            self.retry += 1
            self.get_engine_details(engine_id)
        else:
            raise Exception("Network Error")
        return engine_server

    def update_engine_server(self, engine_id, name, uri, min_loc, max_loc, is_blocked):
        """
        Update an existing engine server's configuration and enables to change certain parameters.
        :param engine_id: int
        :param name: str
        :param uri: str
        :param min_loc: int
        :param max_loc: int
        :param is_blocked: boolean
        :return:
        """
        engine_server = None
        self.engine_server_url = self.engine_server_url.format(id=engine_id)

        post_request_body = CxRegisterEngineRequestBody.CxRegisterEngineRequestBody(
            name=name,
            uri=uri,
            min_loc=min_loc,
            max_loc=max_loc,
            is_blocked=is_blocked
        ).get_post_data()

        r = requests.put(self.engine_server_url, data=post_request_body,
                         headers=AuthenticationAPI.AuthenticationAPI.auth_headers)

        if r.status_code == 200:
            a_dict = r.json()
            engine_server = CxEngineServer.CxEngineServer(
                id=a_dict.get("id"),
                link=CxLink.CxLink(
                    rel=(a_dict.get("link", {}) or {}).get("rel"),
                    uri=(a_dict.get("link", {}) or {}).get("uri")
                )
            )
        elif r.status_code == http.HTTPStatus.BAD_REQUEST:
            raise Exception("Bad Request")
        elif (r.status_code == http.HTTPStatus.UNAUTHORIZED) and (self.retry < 3):
            AuthenticationAPI.AuthenticationAPI.reset_auth_headers()
            self.retry += 1
            self.update_engine_server(engine_id, name, uri, min_loc, max_loc, is_blocked)
        else:
            raise Exception("Network Error")
        return engine_server

    def get_all_engine_configurations(self):
        """
        Get the engine servers configuration list.
        :return:
        """
        all_engine_configurations = None
        r = requests.get(url=self.engine_configurations_url,
                         headers=AuthenticationAPI.AuthenticationAPI.auth_headers)
        if r.status_code == 200:
            a_list = r.json()
            all_engine_configurations = [
                CxEngineConfiguration.CxEngineConfiguration(
                    id=item.get("id"),
                    name=item.get("name")
                ) for item in a_list
            ]
        elif r.status_code == http.HTTPStatus.BAD_REQUEST:
            raise Exception("Bad Request")
        elif (r.status_code == http.HTTPStatus.UNAUTHORIZED) and (self.retry < 3):
            AuthenticationAPI.AuthenticationAPI.reset_auth_headers()
            self.retry += 1
            self.get_all_engine_configurations()
        else:
            raise Exception("Network Error")
        return all_engine_configurations

    def get_engine_configuration_id_by_name(self, engine_configuration_name):
        all_engine_configurations = self.get_all_engine_configurations()
        a_dict = {item.name: item.id for item in all_engine_configurations}
        return a_dict.get(engine_configuration_name)

    def get_engine_configuration_by_id(self, configuration_id):
        """
        Get a specific engine configuration by configuration Id.
        :param configuration_id:
        :return:
        """
        engine_configuration = None
        self.engine_configuration_url = self.engine_configuration_url.format(id=configuration_id)
        r = requests.get(url=self.engine_configuration_url, headers=AuthenticationAPI.AuthenticationAPI.auth_headers)
        if r.status_code == 200:
            a_dict = r.json()
            engine_configuration = CxEngineConfiguration.CxEngineConfiguration(
                    id=a_dict.get("id"),
                    name=a_dict.get("name")
                )
        elif r.status_code == http.HTTPStatus.BAD_REQUEST:
            raise Exception("Bad Request")
        elif (r.status_code == http.HTTPStatus.UNAUTHORIZED) and (self.retry < 3):
            AuthenticationAPI.AuthenticationAPI.reset_auth_headers()
            self.retry += 1
            self.get_engine_configuration_by_id(configuration_id)
        else:
            raise Exception("Network Error")
        return engine_configuration