import json
import google.auth
from google.oauth2 import service_account

from utils import *
from config import *

def key_rotator(request):
    request = request.get_data()
    try: 
        request_json = json.loads(request.decode())
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        return "JSON Error", 400
    service_accounts = request_json.get('service_accounts')
    gcs_dest_path_to_keys = request_json.get('gcs_dest_path_to_keys')
    if not service_accounts:
        service_accounts = DEFAULT_SERVICE_ACCOUNTS
    if not gcs_dest_path_to_keys:
        gcs_dest_path_to_keys = DEFAULT_GCS_LOCATION
    # credentials = google.auth.default()[0]
    # service_account.Credentials.from_service_account_file(
    #     filename=os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
    #     scopes=['https://www.googleapis.com/auth/cloud-platform'])
    for service_account in service_accounts:
        old_key = list_keys(service_account_email=service_account)
        key_json_data = create_key(service_account_email=service_account)
        upload_to_gcs(url=f'{gcs_dest_path_to_keys}{service_account}.json', 
                        data=key_json_data, 
                        content_type="application/octet-stream")
        print(f'Created and uploaded new key.')
        delete_key(full_key_name=old_key["name"])
    return "All keys rotated."