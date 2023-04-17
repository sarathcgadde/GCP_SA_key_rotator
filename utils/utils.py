import base64
import io
from urllib.parse import urlparse

import googleapiclient.discovery
from google.cloud import storage

def create_key(service_account_email, credentials=None):
    """
    Creates a key for a service account.

    Args:
        service_account_email (str): Service account email to create a key for
        credentials (service_account.Credentials, optional): Service account credentials object. Defaults to None.
    """
    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)
    key = service.projects().serviceAccounts().keys().create(
        name='projects/-/serviceAccounts/' + service_account_email, body={}
        ).execute()
    json_key_file = base64.b64decode(key['privateKeyData']).decode('utf-8')
    return json_key_file

def delete_key(full_key_name, credentials=None):
    """
    Deletes a service account key.

    Args:
        full_key_name (str): Full key name in the form of 'projects/<project>/serviceAccounts/<service account email>/keys/<key id>'
        credentials (service_account.Credentials, optional): Service account credentials object. Defaults to None.
    """
    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)
    service.projects().serviceAccounts().keys().delete(
        name=full_key_name).execute()
    print('Deleted key: ' + full_key_name)

def list_keys(service_account_email, credentials=None):
    """
    Lists all keys for a service account.

    Args:
        service_account_email (str): Service account email to list keys for
        credentials (service_account.Credentials, optional): Service account credentials object. Defaults to None.

    Returns:
        dict: Key dictionary corresponding to active user managed key
    """
    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)
    keys = service.projects().serviceAccounts().keys().list(
        name='projects/-/serviceAccounts/' + service_account_email).execute()
    for key in keys['keys']:
        if key['keyType'] == 'USER_MANAGED' and not key.get('disabled'):
            return key

class GCSUrl(object):
    def __init__(self, url: str):
        """GCS url

        Args:
            url (str): Fully qualified gsc url
        """
        self._parsed = urlparse(url, allow_fragments=False)

    @property
    def bucket(self) -> str:
        """Get bucket name

        Returns:
            str: Bucket name
        """
        return self._parsed.netloc

    @property
    def path(self) -> str:
        """Blob file path

        Returns:
            str: File path
        """
        if self._parsed.query:
            return self._parsed.path.lstrip('/') + '?' + self._parsed.query
        else:
            return self._parsed.path.lstrip('/')

    @property
    def url(self) -> str:
        """Fully qualified GCS url

        Returns:
            str: GCS url
        """
        return self._parsed.geturl()

    def __repr__(self):
        return f'GCSUrl({self.url})'

    def __str__(self):
        return self.url

def upload_to_gcs(url: str, data: bytes, credentials=None, content_type='text/plain'):
        """
        Upload bytes data to gcs

        Args:
            url (str): file path to upload the data
            data (bytes): Data to upload to GCS
            content_type (str, optional): Type of file to upload. Defaults to 'text/plain'.
        """
        url = GCSUrl(url)
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(url.bucket)
        blob = bucket.blob(url.path)
        if type(data) == io.BytesIO:
            blob.upload_from_file(data, content_type=content_type)
        else:
            blob.upload_from_string(data, content_type=content_type)