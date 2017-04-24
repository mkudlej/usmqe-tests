"""
REST API test suite - ceph cluster import

"""
import pytest

from usmqe.api.tendrlapi import cephapi


LOGGER = pytest.get_logger('ceph_import_test', module=True)
"""@pylatest default
Setup
=====
"""

"""@pylatest default
Teardown
========

"""

"""@pylatest api/ceph.cluster_import
API-ceph: cluster_import
***************************

.. test_metadata:: author mkudlej@redhat.com

Description
===========

Positive import Ceph cluster.

"""


def test_cluster_import_valid(valid_session_credentials):
    """@pylatest api/ceph.cluster_import
        .. test_step:: 1

        Get list of ids of availible nodes.

        .. test_result:: 1

                Server should return response in JSON format:

                        {
                ...
                  {
                  "fqdn": hostname,
                  "machine_id": some_id,
                  "node_id": node_id
                  },
                ...
                        }

                Return code should be **200** with data ``{"message": "OK"}``.

        """
    api = cephapi.TendrlApiCeph(auth=valid_session_credentials)
    """@pylatest api/ceph.cluster_import
        .. test_step:: 2

            Send POST request to Tendrl API ``APIURL/CephImportCluster

        .. test_result:: 2

            Server should return response in JSON format:

                {
                  "job_id": job_id
                }

            Return code should be **202** with data ``{"message": "Accepted"}``.

        """
    nodes = api.get_nodes()

    ceph_nodes = [node["node_id"] for node in nodes["nodes"] if "ceph" in node["tags"]]
    LOGGER.debug("Nodes for importing: {}".format(ceph_nodes))
    cluster_data = {
        "node_ids": ceph_nodes,
        "sds_type": "ceph"
    }

    job_id = api.import_cluster(cluster_data)["job_id"]

    api.wait_for_job_status(job_id, max_count=200)

    integration_id = api.get_job_attribute(
        job_id=job_id,
        attribute="TendrlContext.integration_id",
        section="parameters")

    LOGGER.debug("integration_id: %s" % integration_id)
    pytest.check(
        [x for x in api.get_cluster_list() if x["integration_id"] == integration_id],
        "Job list integration_id '{}' should be present in cluster list.".format(integration_id),
        issue="https://github.com/Tendrl/api/issues/154")

    # TODO add test case for checking imported machines