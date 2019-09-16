import logging
import json
import requests
from collections import OrderedDict

LOG = logging.getLogger()


class ElasticsearchOutputBackend:
    """Elasticsearch output backend class"""

    def __init__(self, elastic_host):
        self.s = requests.Session()
        self.elastic_host = elastic_host

    def close(self):
        pass

    def push(self, counters):
        for counter in counters:
            elastic_document = OrderedDict()
            elastic_document["timestamp"] = counter.timestamp
            elastic_document["job_id"] = counter.job_id
            elastic_document["hostname"] = counter.hostname
            elastic_document = json.dumps({**elastic_document, **counter.metrics})
            print("\n Elastic document", elastic_document)
            self.index_document(elastic_document, counter.backend_name.lower())


    def index_document(self, elastic_document, index):
        """Index document in Elasticsearch using its http api"""
        elastic_host = self.elastic_host
        self.create_index_if_necessary(index)
        url = "{elastic_host}/{index}/_doc/".format(elastic_host=elastic_host, index=index)
        headers = {"Content-Type": "application/json"}
        r = self.s.post(url=url, headers=headers, data=elastic_document)

    def create_index_if_necessary(self, index):
        elastic_host = self.elastic_host
        url = "{elastic_host}/{index}".format(elastic_host=elastic_host, index=index)
        r = self.s.head(url)
        if r.status_code ==404:  # create nex index
            mapping = {
                "mappings": {
                    "properties": {
                        "timestamp": {
                            "type": "date",
                            "format": "epoch_second"
                        }
                    }
                }
            }
            mapping = json.dumps(mapping)
            headers = {"Content-Type": "application/json"}
            url = "{elastic_host}/{index}".format(elastic_host=elastic_host, index=index)
            r = self.s.put(url=url, headers=headers, data=mapping)