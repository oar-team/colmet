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
                            37: "cpu_cycles", # Perfhw
                            38: "instructions",
                            39: "cache_references",
                            40: "cache_misses",
                            41: "branch_instructions",
                            42: "branch_misses",
                            43: "bus_cycles",
                            44: "ref_cpu_cycles",
                            45: "cache_l1d",
                            46: "cache_ll",
                            47: "c ache_dtlb",
                            48: "cache_itlb",
                            49: "cache_bpu",
                            50: "cache_node",
                            51: "cache_op_read",
                            52: "cache_op_prefetch",
                            53: "cache_result_access",
                            54: "cpu_clock",
                            55: "task_clock",
                            56: "page_faults",
                            57: "context_switches",
                            58: "cpu_migrations",
                            59: "page_faults_min",
                            60: "page_faults_maj",
                            61: "alignment_faults",
                            62: "emulation_faults",
                            63: "dummy",
                            64: "bpf_output"
                 }


class Counter:
    def __init__(self, hostname, timestamp, job_id, backend_name, metrics):
        self.hostname = hostname
        self.timestamp = timestamp
        self.job_id = job_id
        self.backend_name = backend_name
        self.metrics = metrics


class CounterFactory:
    def __init__(self, data):
        self.counters = []
        for job_id, tmp in data[0].items():
            self.hostname = tmp[0].decode('utf-8')
            self.timestamp = tmp[1]
            self.job_id = job_id
            for backend in tmp[2]:
                self.backend_name = backend[0].decode('utf-8')
                tmp = backend[1]
                self.metric_names = []
                for compressed_metric_name in tmp:
                    self.metric_names.append(METRICS_NAMES[compressed_metric_name])
                self.metric_values = backend[2]
                self.backend_metrics = dict(zip(self.metric_names, self.metric_values))
                counter = Counter(self.hostname, self.timestamp, self.job_id, self.backend_name, self.backend_metrics)
                self.counters.append(counter)

    def get_counters(self):
        return self.counters
