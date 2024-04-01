from simple_rest_client.api import API
import chime.naas.apis

from automation.AutomationAPI import AutomationAPI


class AutomationApi:
    api: API

    def __init__(
            self,
            api_root_url=None,
            timeout=None,
            headers=None,
            ssl_verify=None
    ):
        self.api = API(
            api_root_url=api_root_url,
            params={},
            headers=headers,
            timeout=timeout,
            append_slash=False,
            json_encode_body=True,
            ssl_verify=ssl_verify
        )

        self.api.add_resource(resource_name='task', resource_class=AutomationAPI)
