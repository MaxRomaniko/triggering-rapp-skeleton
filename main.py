import time
import json
from utils.logger_config import logger
from utils.context import context
from utils.api_init import naas
from utils.api_init import automation
from utils.api_init import pca

def update_status(tracking_id, status, data={}):
    try:
        flow_status = {}
        flow_status['status'] = status
        if data:
            flow_status['data'] = data
        pca.api.contextual_automation_flow_service.update_contextual_automation_flow(tracking_id, body=flow_status)
    except Exception as e:
        logger.error("Failed to update status", e)

def start_task(naas_cluster, task_id, parent_tracking_id):
    run_task_body = {}
    run_task_body['ignoreConcurrency'] = 'true'
    run_task_body['clusterName'] = naas_cluster
    run_task_body['parentTrackingId'] = parent_tracking_id

    tracking_info = automation.api.task.run_task(task_id, body=run_task_body)
    return tracking_info.body['trackingId']

def await_completion(task_id, tracking_id, timeout_seconds):
    start_time = time.time()
    job_status = 'PENDING'
    while job_status != 'COMPLETED' and job_status != 'ERROR' and job_status != 'INTERRUPTED' \
            and time.time() < start_time + timeout_seconds:
        time.sleep(1)
        job_info = automation.api.task.instances(task_id, params={'trackingId': tracking_id})
        if not job_info.body['instances']:
            return 'ERROR'
        job_status = job_info.body['instances'][0]['instance']['state']
    return job_status

def find_attribute(json_data, target_attribute):
    """
    Recursively searches for the target attribute within the JSON data.
    :param json_data: A dictionary representing the JSON data.
    :param target_attribute: The attribute you want to extract.
    :return: A list of values corresponding to the target attribute.
    """
    result = []
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == target_attribute:
                result.append(value)
            elif isinstance(value, (dict, list)):
                result.extend(find_attribute(value, target_attribute))
    elif isinstance(json_data, list):
        for item in json_data:
            result.extend(find_attribute(item, target_attribute))

    return result

def load_cluster_cells(cluster_name):
    cluster_cells_response = naas.api.clusters.get_cluster_cells(cluster_name, params={'fields': '_id', 'includeExtensions': 'false', 'links': 'false'})
    cluster_cells = cluster_cells_response.body['elements']
    while cluster_cells_response.body['pagination']['continuationId'] != 'Last Page':
        continuation_id = cluster_cells_response.body['pagination']['continuationId']
        cluster_cells_response = naas.api.cells.get_cells(params={'continuationId': continuation_id, 'links': 'false', 'fields': '_id'})
        cluster_cells = cluster_cells + cluster_cells_response.body['elements']
    ids = [obj['cell']['_id'] for obj in cluster_cells]
    return ids

def create_new_cluster(cluster_name, controller_unique_id):
    cluster = {}
    try:
        cluster = naas.api.clusters.get_cluster_by_name(cluster_name)
    except Exception as e:
        logger.info("Cluster " + cluster_name + " does not exist. Creating...", e)
    if not cluster:
        cluster = naas.api.clusters.create_cluster(body={'name': cluster_name, 'cellsCriteria': {'controllerUniqueId':controller_unique_id}})


def convertToDict(event):
    try:
        event = event.replace('\\r','')
        event = event.replace('\r','')
        event = event.replace('\\n','')
        event = event.replace('\n','')
        event = event.replace('\\t','')
        event = event.replace('\t','')
        event = event.replace('\\"','"')
        event = event.replace('\"','"')
        if event.startswith('"') and event.endswith('"'):
            event = event[1:-1]
        return json.loads(str(event))
    except Exception as e:
        logger.info("Failed to parse event. Taking as string", e)
        return event


def main():
    logger.info("Getting Started with Contextual Automation service skeleton app")
    logger.info("Application will try to parse EVENT and search for configurationItem attribute")
    logger.info("If attribute is found new naas cluster will be created with the name CONTROLLERNAME_[eNodB]")
    logger.info("Then task with TASK_ID will be started with created cluster")
    logger.info("Application will wait for task to finish and then return status to pca")

    tracking_id = context['TRACKING_ID']
    try:
        event = context['EVENT']
        if(isinstance(event, str)):
            event = convertToDict(event)

        logger.info("Result event type " + str(type(event)))
        logger.info("Received an event " + str(event))
        e_node_b = find_attribute(event, "configurationItem")
        if not e_node_b:
            logger.info("EnodeB not found in the event " + str(event))
            response_payload = {}
            response_payload['ErrorMessage'] = 'EnodeB not found in the event'
            update_status(tracking_id, 'FAILED', response_payload)
            return

        controller = naas.api.controllers.get_controllers(params={'name': e_node_b, 'includeExtensions': 'false', 'links': 'false'})
        if not controller.body['elements']:
            logger.info("Controller not found in the network " + str(event))
            response_payload = {}
            response_payload['ErrorMessage'] = 'Controller not found in the network'
            update_status(tracking_id, 'FAILED', response_payload)
            return

        controller_unique_id = controller.body['elements'][0]['controller']['_id']

        new_cluster_name = 'CONTROLLERNAME_' + e_node_b[0]
        create_new_cluster(new_cluster_name, controller_unique_id)

        cluster_cells = load_cluster_cells(new_cluster_name)

        logger.info("Starting app with tracking id " + tracking_id)
        logger.info("Cluster is: " + new_cluster_name)

        task_id = context['TASK_ID']
        logger.info("Starting SON task with id " + str(task_id))
        subtask_tracking_id = start_task(new_cluster_name, task_id, tracking_id)

        logger.info("Started SON task with id " + str(task_id) + ", tracking id " + subtask_tracking_id)
        job_status = await_completion(task_id, subtask_tracking_id, 3600)
        logger.info("Job ended with status: " + job_status)

        response_payload = {}
        response_payload['job_status'] = job_status
        response_payload['cluster'] = new_cluster_name
        response_payload['population'] = cluster_cells
        update_status(tracking_id, 'COMPLETED', response_payload)
    except Exception as e:
        logger.info("Task execution failed", e)
        update_status(tracking_id, 'FAILED')

if __name__ == '__main__':
    main()
