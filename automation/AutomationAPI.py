from simple_rest_client.resource import Resource

class AutomationAPI(Resource):
    actions = {
        "run_task": {"method": "POST", "url": "/v1/tasks/{}/run", },
        "instances": {"method": "GET", "url": "/v1/tasks/{}/instances"}
    }
