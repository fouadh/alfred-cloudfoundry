from cloudfoundry_client.client import CloudFoundryClient


def get_apps(wf, target):
    client = CloudFoundryClient(target["endpoint"], verify=False)
    client.init_with_user_credentials(target["login"], target["password"])
    manager = client.v2.apps
    size = 0

    for item in manager:
        wf.add_item(title=item["entity"]["name"], subtitle=item["entity"]["state"])
        size = size + 1

    if size == 0:
        wf.add_item(title="No application found")
