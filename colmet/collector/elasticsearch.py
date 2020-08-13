import logging
import json
import requests
from collections import OrderedDict
from ..common.backends.base import OutputBaseBackend

LOG = logging.getLogger("Elastic Backend")

class ElasticsearchOutputBackend(OutputBaseBackend):
    """Elasticsearch output backend class"""
    __backend_name__ = "elasticsearch"

    def open(self):
        self.s = requests.Session()
        LOG.debug("Elasticsearch session opened")

    def close(self):
        self.s.close()
        LOG.debug("Elasticsearch session closed")

    def push(self, counters_list):
        """Push the metrics in Elasticsearch database"""
        indices=[]
        bulk=''
        c=0
        elastic_index_prefix = self.options.elastic_index_prefix
        for counter in counters_list:
            elastic_document = OrderedDict()
            metric_backend_value = None
            for counter_header in list(counter._header_definitions):  # add job_id, hostname, timestamp
                counter_header_value = counter._get_header(counter_header)
                if counter_header == "metric_backend":
                    metric_backend_value = counter_header_value.lower()  # name of the backend that is used as index is Elasticsearch
                    if elastic_index_prefix+metric_backend_value not in indices:
                        indices.append(elastic_index_prefix+metric_backend_value)
                else:
                    elastic_document[counter_header] = counter_header_value
            for counter_metric in list(counter._counter_definitions):  # add metric values
                counter_metric_value = counter._get_counter(counter_metric)
                # Convert strings that are json
                try:
                    value = json.loads(counter_metric_value)
                    counter_metric_value = value
                except:
                    pass
                elastic_document[counter_metric] = counter_metric_value
            #elastic_document = json.dumps(elastic_document, indent=2)
            #self.index_document(elastic_document, index=metric_backend_value)
            bulk+='{ "create" : { "_index" : "'+elastic_index_prefix+metric_backend_value+'" }}\n'
            bulk+=json.dumps(elastic_document, indent=None)+'\n'
            c+=1
        self.open()
        for index in indices:
            self.create_index_if_necessary(index)
        LOG.info("Elastic: indexing %s docs" % c)
        self.index_bulk(bulk)
        self.close()

    def index_bulk(self, bulk):
        """Do a bulk indexing into elasticsearch"""
        elastic_host = self.options.elastic_host
        url = "{elastic_host}/_bulk/".format(elastic_host=elastic_host)
        headers = {"Content-Type": "application/x-ndjson"}
        r = self.s.post(url=url, headers=headers, data=bulk)
        if r.status_code != 200:
            LOG.warning("Got http error from elastic: %s %s" , r.status_code , r.text)
        response=json.loads(r.text)
        if response["errors"]:
            LOG.warning("Elastic status is ERROR!")
            for item in response["items"]:
                for key in item:
                    it=item[key]
                    if it["status"] != 201 :
                        LOG.warning("Status %s for %s action:", it["status"], key)
                        LOG.warning(json.dumps(item[key]))
        else:
            LOG.debug("Elastic bulk push ok: took %s ms" , response["took"])

    def create_index_if_necessary(self, index):
        elastic_host = self.options.elastic_host
        url = "{elastic_host}/{index}".format(elastic_host=elastic_host, index=index)
        r = self.s.head(url)
        if r.status_code ==404:  # create new index
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
            LOG.info("Elastic: created missing index %s" % index)
            r = self.s.put(url=url, headers=headers, data=mapping)
