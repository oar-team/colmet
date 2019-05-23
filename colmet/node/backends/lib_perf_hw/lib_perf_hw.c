/*******************************************************
 * Copyright (C) 2018 Georges Da Costa <georges.da-costa@irit.fr>
 *******************************************************/

#include <linux/perf_event.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <stdio.h>
#include <stdint.h>
#include <asm/unistd.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

typedef struct _counter_t* counter_t;

struct _counter_t {
  int nbcores;
  int nbperf;
  int **counters;
};

counter_t g_counter;

counter_t init_counters();
void clean_counters();
void start_counters();
void reset_counters();
void get_counters(long long *values);

const int nb_perf = 3;
const char* perf_names[3] = {"instructions", "cachemisses", "pagefaults"};
const __u32 perf_type[3] = {PERF_TYPE_HARDWARE,PERF_TYPE_HARDWARE,PERF_TYPE_SOFTWARE};
const __u64 perf_key[3] = {PERF_COUNT_HW_INSTRUCTIONS, PERF_COUNT_HW_CACHE_MISSES, PERF_COUNT_SW_PAGE_FAULTS};

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
		int cpu, int group_fd, unsigned long flags) {
  long res = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
  if (res == -1) {
    perror("perf_event_open");
    fprintf(stderr, "Error opening leader %llx\n", hw_event->config);
    exit(EXIT_FAILURE);
  }
  return res;
}

char* concat(const char *s1, const char *s2)
{
    char *result = malloc(strlen(s1) + strlen(s2) + 1); // +1 for the null-terminator
    if(result == NULL)
      return;
    strcpy(result, s1);
    strcat(result, s2);
    return result;
}

counter_t init_counters(char * job_name) {
  struct perf_event_attr pe;
  unsigned int nbcores = sysconf(_SC_NPROCESSORS_ONLN);
  memset(&pe, 0, sizeof(struct perf_event_attr));
  pe.size = sizeof(struct perf_event_attr);
  pe.disabled = 1;

  char * filename = concat("/sys/fs/cgroup/perf_event", job_name); 
  int fd1 = open(filename, O_RDONLY);
  if(fd1 == NULL){
    return 0;
  }
  printf("Gathering infos for: %s\n", filename);

  g_counter = malloc(sizeof(struct _counter_t));
  g_counter->nbperf = nb_perf;
  g_counter->nbcores=nbcores;
  g_counter->counters=malloc(nb_perf*sizeof(int*));
  for (int i=0; i<nb_perf; i++) {
    pe.type = perf_type[i];
    pe.config = perf_key[i];
    g_counter->counters[i] = malloc(nbcores*sizeof(int));

    //loop on cores because per-cgroup monitoring is not available with cpu = -1 : https://stackoverflow.com/questions/52892668/using-perf-event-open-to-monitor-docker-containers
    //in cgroup-mode the event is measured only if the thread running on the monitored CPU belongs to the designated cgroup http://man7.org/linux/man-pages/man2/perf_event_open.2.html (should we test that ?)
    for (int core=0; core<nbcores; core++) {
      g_counter->counters[i][core] = perf_event_open(&pe, fd1, core, -1, PERF_FLAG_PID_CGROUP|PERF_FLAG_FD_CLOEXEC);
    }
  }
}

void clean_counters() {
  for(int counter=0; counter<g_counter->nbperf; counter++) {
    for(int core=0; core<g_counter->nbcores; core++)
      close(g_counter->counters[counter][core]);
    free(g_counter->counters[counter]);
  }
  free(g_counter->counters);
  free(g_counter);
}

void start_counters() {
  for(int counter=0; counter<g_counter->nbperf; counter++)
    for(int core=0; core<g_counter->nbcores; core++)
      ioctl(g_counter->counters[counter][core], PERF_EVENT_IOC_ENABLE, 0);
}
void reset_counters() {
  for(int counter=0; counter<g_counter->nbperf; counter++)
    for(int core=0; core<g_counter->nbcores; core++)
      ioctl(g_counter->counters[counter][core], PERF_EVENT_IOC_RESET, 0);
}

void get_counters(long long *values) {
  for(int i=0; i<g_counter->nbperf; i++) {
    long long accu=0;
    long long count;
    for (int core=0; core<g_counter->nbcores; core++) {
      if (-1 == read(g_counter->counters[i][core], &count, sizeof(long long))) {
        fprintf(stderr, "PB Lecture resultat");
        exit(EXIT_FAILURE);
      }
      accu += count;
    }
    values[i] = accu;
  }
  reset_counters(g_counter);
}
