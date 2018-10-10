def test_auth():
    """
    Copied from GCP Getting started. Helper that makes an authenticated call to test credentials.
    Exception should be caught by caller
    """
    from google.cloud import storage

    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    storage_client = storage.Client()

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())

