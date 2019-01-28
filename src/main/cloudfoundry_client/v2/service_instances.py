from cloudfoundry_client.v2.entities import EntityManager
from cloudfoundry_client.json_object import JsonObject


class ServiceInstanceManager(EntityManager):
    list_query_parameters = ['page', 'results-per-page', 'order-direction', 'return_user_provided_service_instances']

    def __init__(self, target_endpoint, client):
        super(ServiceInstanceManager, self).__init__(target_endpoint, client, '/v2/service_instances')

    def create(self, space_guid, instance_name, plan_guid, parameters=None, tags=None):
        request = self._request(name=instance_name, space_guid=space_guid, service_plan_guid=plan_guid)
        request['parameters'] = parameters
        request['tags'] = tags
        return super(ServiceInstanceManager, self)._create(request)

    def update(self, instance_guid, instance_name=None, plan_guid=None, parameters=None, tags=None):
        request = self._request()
        request['name'] = instance_name
        request['service_plan_guid'] = plan_guid
        request['parameters'] = parameters
        request['tags'] = tags
        return super(ServiceInstanceManager, self)._update(instance_guid, request)

    def list_permissions(self, instance_guid):
        return super(ServiceInstanceManager, self)._get('%s/%s/permissions' % (self.entity_uri, instance_guid),
                                                        JsonObject)

    def remove(self, instance_guid):
        super(ServiceInstanceManager, self)._remove(instance_guid)
