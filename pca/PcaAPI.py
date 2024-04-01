from simple_rest_client.resource import Resource

class PcaAPI(Resource):
    actions = {
        "update_contextual_automation_flow": {"method": "PUT", "url": "/v1/contextual-automation-flow/{}", }
    }
