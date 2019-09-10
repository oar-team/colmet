import os
import re
import time


from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job
from colmet.common.metrics.temperaturestats import TemperaturestatsCounters


class TemperaturestatsBackend(InputBaseBackend):
    __backend_name__ = "temperaturestats"

    def open(self):
        self.temperaturestats = TemperatureStats(self.options)
        # job with id equal to 0 is the fictive job to gather nodes' monitoring
        # measures
        self.job_0 = Job(self, 0, self.options)

    def close(self):
        pass

    def get_temperaturestats(self):
        counters = self.temperaturestats.get_stats()
        return counters

    def get_counters_class(self):
        return TemperaturestatsCounters

    def pull(self):
        self.job_0.update_stats()
        return self.job_0.get_stats()


class TemperatureStats(object):

    def __init__(self, option):
        self.options = option

        metrics_mapping = open("./temperature_mapping." + str(time.time()) + ".csv", "w+")

        for i in range(6):
            try:
                f = open("/sys/class/thermal/thermal_zone" + str(i) + "/type", "r")
                metrics_mapping.write("counter_" + str(i + 1) + ", " + str(f.readline()).rstrip() + "_" + str(i) + "\n")
            except FileNotFoundError:
                metrics_mapping.write("counter_" + str(i + 1) + ", " + "no counter \n")

    def get_stats(self):

        temperaturestats_data = {}

        for i in range(6):
            try:
                f = open("/sys/class/thermal/thermal_zone" + str(i) + "/temp", "r")
                # print("ok", f.readline())
                temperaturestats_data["counter_" + str(i+1)] = int(int(f.readline())/1000)
            except FileNotFoundError:
                temperaturestats_data["counter_" + str(i+1)] = -1

        return TemperaturestatsCounters(temperaturestats_buffer=temperaturestats_data)
