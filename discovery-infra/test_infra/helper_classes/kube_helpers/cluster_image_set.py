import logging

from pprint import pformat

import yaml
from kubernetes.client import ApiClient, CustomObjectsApi
from tests.conftest import env_variables

from .base_resource import BaseResource

logger = logging.getLogger(__name__)


class ClusterImageSetReference:
    """
    A CRD that represents a reference for a ClusterImageSet resource.
    The reference contains only the name of the ClusterImageSet,
    so the assisted-service could fetch the resource accordingly.
    """
    def __init__(
            self,
            name: str,
    ):
        self.name = name

    def __repr__(self) -> str:
        return str(self.as_dict())

    def as_dict(self) -> dict:
        data = {
            'name': self.name,
        }
        return data


class ClusterImageSet(BaseResource):
    """
    A CRD that represents a ClusterImageSet resource that contains the release image URI.
    Upon creating a cluster deployment, the release image is fetched by the assisted-service
    from the image set.
    """

    _api_group = 'hive.openshift.io'
    _api_version = 'v1'
    _plural = 'clusterimagesets'

    def __init__(
            self,
            kube_api_client: ApiClient,
            name: str,
            namespace: str = env_variables['namespace'],
    ):
        super().__init__(name, namespace)
        self.crd_api = CustomObjectsApi(kube_api_client)

    def create_from_yaml(self, yaml_data: dict) -> None:
        self.crd_api.create_cluster_custom_object(
            group=self._api_group,
            version=self._api_version,
            plural=self._plural,
            body=yaml_data,
        )

        logger.info(
            'created cluster imageset %s: %s', self.ref, pformat(yaml_data)
        )

    def create(
            self,
            releaseImage: str
    ):
        body = {
            'apiVersion': f'{self._api_group}/{self._api_version}',
            'kind': 'ClusterImageSet',
            'metadata': self.ref.as_dict(),
            'spec': {
                'releaseImage': releaseImage,
            }
        }
        self.crd_api.create_cluster_custom_object(
            group=self._api_group,
            version=self._api_version,
            plural=self._plural,
            body=body,
        )

        logger.info(
            'created cluster imageset %s: %s', self.ref, pformat(body)
        )

    def get(self) -> dict:
        return self.crd_api.get_namespaced_custom_object(
            group=self._api_group,
            version=self._api_version,
            plural=self._plural,
            name=self.ref.name,
            namespace=self.ref.namespace,
        )

    def delete(self) -> None:
        self.crd_api.delete_namespaced_custom_object(
            group=self._api_group,
            version=self._api_version,
            plural=self._plural,
            name=self.ref.name,
            namespace=self.ref.namespace,
        )

        logger.info('deleted cluster imageset %s', self.ref)