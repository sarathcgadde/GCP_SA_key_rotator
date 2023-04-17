# GCP_SA_key_rotator
Simple implementation of SA Key Rotation on GCP.

1. Update the Config file under (config/) with the service accounts to rotate keys for and the GCS bucket to store keys in.
2. Create a Service Account for your cloud function that has the following roles:
    - Cloud Functions Invoker
    - Service Account Key Admin
    - Storage Object Admin with Conditional access to the bucket
        - resource.name.startsWith('projects/_/buckets/<your_bucket_name>')
3. Create a Cloud function using the zipped module.
4. Create a Schedule on Cloud scheduler based on rotation policy and select HTTP POST as target request type, and input the Cloud function endpoint.
    - Pass the {"service_accounts": [], "gcs_dest_path_to_keys": ""} to Body field and update as necessary.
    - Select Add OIDC token for Auth Header and select the Service Account created above to invoke the Cloud function.
    <img width="487" alt="Screenshot 2023-04-17 at 12 17 03" src="https://user-images.githubusercontent.com/73820831/232469394-2450d5df-85b4-4ac0-917a-5ad8765060df.png">
