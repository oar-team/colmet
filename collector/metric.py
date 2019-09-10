METRICS_NAMES = {1: "cache",  # Memory backend
                            2: "rss",
                            3: "rss_huge",
                            4: "shmem",
                            5: "mapped_file",
                            6: "dirty",
                            7: "writeback",
                            8: "pgpgin",
                            9: "pgpgout",
                            10: "pgfault",
                            11: "pgmajfault",
                            12: "inactive_anon",
                            13: "active_anon",
                            14: "inactive_file",
                            15: "active_file",
                            16: "unevictable",
                            17: "hierarchical_memory_limit",
                            18: "total_cache",
                            19: "total_rss",
                            20: "total_rss_huge",
                            21: "total_shmem",
                            22: "total_mapped_file",
                            23: "total_dirty",
                            24: "total_writeback",
                            25: "total_pgpgin",
                            26: "total_pgpgout",
                            27: "total_pgfault",
                            28: "total_pgmajfault",
                            29: "total_inactive_anon",
                            30: "total_active_anon",
                            31: "total_inactive_file",
                            32: "total_active_file",
                            33: "total_unevictable",
                            34: "nr_periods",  # Cpu Backend
                            35: "nr_throttled",
                            36: "throttled_time",
                            }

class Metric:
    def __init__(self, hostname, timestamp, job_id, backend_name, metrics):
        self.hostname = hostname
        self.timestamp = timestamp
        self.job_id = job_id
        self.backend_name = backend_name
        self.metrics = metrics


class MetricFactory:
    def __init__(self, data):
        self.metrics = []
        for job_id, tmp in data[0].items():
            self.hostname = str(tmp[0])
            self.timestamp = tmp[1]
            self.job_id = job_id
            for backend in tmp[2]:
                self.backend_name = backend[0]
                tmp = backend[1]
                self.metric_names = []
                for compressed_metric_name in tmp:
                    self.metric_names.append(METRICS_NAMES[compressed_metric_name])
                self.metric_values = backend[2]
                self.backend_metrics = dict(zip(self.metric_names, self.metric_values))
                metric = Metric(self.hostname, self.timestamp, self.job_id, self.backend_name, self.backend_metrics)
                self.metrics.append(metric)

    def get_metrics(self):
        return self.metrics
