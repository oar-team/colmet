import logging
import json
import requests
from collections import OrderedDict
from ..common.backends.base import OutputBaseBackend

LOG = logging.getLogger()


class ElasticsearchOutputBackend(OutputBaseBackend):
    """Elasticsearch output backend class"""
    __backend_name__ = "elasticsearch"

    def open(self):
        pass

    def close(self):
        pass

    def push(self, counters_list):
        """Push the metrics in Elasticsearch database"""
        for counter in counters_list:
            elastic_document = OrderedDict()
            metric_backend_value = None
            for counter_header in list(counter._header_definitions):  # add job_id, hostname, timestamp
                counter_header_value = counter._get_header(counter_header)
                if counter_header == "metric_backend":
                    metric_backend_value = counter_header_value.lower()  # name of the backend that is used as index is Elasticsearch
                else:
                    elastic_document[counter_header] = counter_header_value
            for counter_metric in list(counter._counter_definitions):  # add metric values
                counter_metric_value = counter._get_counter(counter_metric)
                elastic_document[counter_metric] = counter_metric_value
            elastic_document = json.dumps(elastic_document, indent=2)
            self.index_document(elastic_document, index=metric_backend_value)

    def index_document(self, elastic_document, index):
        """Index document in Elasticsearch using its http api"""
        elastic_host = self.options.elastic_host
        self.create_index_if_necessary(index)
        url = "{elastic_host}/{index}/_doc/".format(elastic_host=elastic_host, index=index)
        headers = {"Content-Type": "application/json"}
        r = requests.post(url=url, headers=headers, data=elastic_document)

    def create_index_if_necessary(self, index):
        elastic_host = self.options.elastic_host
        url = "{elastic_host}/{index}".format(elastic_host=elastic_host, index=index)
        r = requests.head(url)
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
            r = requests.put(url=url, headers=headers, data=mapping)
