
# CHIME Developer Python Application

## Getting Started

### Introduction
Getting Started with Contextual Automation service skeleton app
Application will try to parse EVENT and search for eNodeB attribute
If attribute is found new naas cluster will be created with the name CONTROLLERNAME_[eNodB]
Then task with TASK_ID will be started with created cluster
Application will wait for task to finish and then return status to pca

### Quick Start
The following instructions explain how to configure your URLs and call your first CHIME API.

<b>To call your first CHIME API, simply do as follows:</b>

* Configure API urls in <b>utils/api_init.py</b>

  ```python
    # Configure CHIME Services endpoints
    NAAS_URL = 'https://edgewise.qualcomm.com/naas'
    AUTOMATION_URL = 'https://edgewise.qualcomm.com/automation'
    PCA_URL = 'https://edgewise.qualcomm.com/contextual-automation-service'
    AUTH_URL = 'https://edgewise.qualcomm.com/edgewise/oauth/token'
