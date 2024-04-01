from chime.client.naas import NaaSApi
from chime.client.pgw import PGWApi
from chime.client.xpaas import XPaaSApi
from client.automation import AutomationApi
from client.pca import PcaApi
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from utils.context import context
import os


# Configure CHIME Services endpoints
AUTH_URL = os.environ.get('AUTH_HOST', 'https://edgewise.qualcomm.com/edgewise/oauth/token')
NAAS_URL = "os.environ['NAAS_HOST']"#'https://edgewise.qualcomm.com/naas'
AUTOMATION_URL = "os.environ['AUTOMATION_HOST']"
PCA_URL = "os.environ['PCA_HOST']"

# Configure Client_Id and Client_Secret to enable authentication
CLIENT_ID = None
CLIENT_SECRET = None

HEADERS = {}

# CHIME uses Oauth2 client credentials authentication flow
if CLIENT_ID is not None and CLIENT_SECRET is not None:
    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=AUTH_URL, client_id=CLIENT_ID,
                              client_secret=CLIENT_SECRET, verify=True)

    # init API client headers with access_token
    HEADERS = {'Authorization': 'Bearer ' + token.get('access_token')}

# Init  clients
naas = NaaSApi(api_root_url=NAAS_URL, timeout=60, headers=HEADERS)
automation = AutomationApi(api_root_url=AUTOMATION_URL, timeout=60, headers=HEADERS)
pca = PcaApi(api_root_url=PCA_URL, timeout=60, headers=HEADERS)
