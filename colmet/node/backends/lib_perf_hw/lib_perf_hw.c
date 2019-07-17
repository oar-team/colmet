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
#include <errno.h>
#include <stdbool.h>


/* represent a perf_event counter, it is initialized by syscall perf_event_open */
typedef struct _counter_t* counter_t;
struct _counter_t {
  int nbcores;
  int nbperf;
  int **counters;
};

/* represent a perf_event cgroup
cgroup_name : name of the cgroup
g_counter : perf_event counter associated to the cgroup
next : reference to the next cgroup in the linked list of cgroups */
typedef struct _cgroup_t *cgroup_t;
struct _cgroup_t {
   char *cgroup_name;
   counter_t g_counter;
   struct _cgroup_t *next;
};

/* initialize a linked list of perf_event cgroups */
cgroup_t head = NULL;
cgroup_t current = NULL;

cgroup_t find(char *cgroup_name);
void insertFirst(char *cgroup_name, counter_t g_counter);
void remove_cgroup(char *cgroup_name);

const int nb_perf = 3;
const char* perf_names[3] = {"instructions", "cachemisses", "pagefaults"};
const __u32 perf_type[3] = {PERF_TYPE_HARDWARE,PERF_TYPE_HARDWARE,PERF_TYPE_SOFTWARE};
const __u64 perf_key[3] = {PERF_COUNT_HW_INSTRUCTIONS, PERF_COUNT_HW_CACHE_MISSES, PERF_COUNT_SW_PAGE_FAULTS};

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
		int cpu, int group_fd, unsigned long flags) {
  long res = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);

  if (res == -1) {
    fprintf(stderr, "Error opening leader %llx %d\n", hw_event->config, errno);
  }
  return res;
}

char* concat(const char *s1, const char *s2)
{
    char *result = malloc(strlen(s1) + strlen(s2) + 1); // +1 for the null-terminator
    if(result == NULL)
      return NULL;
    strcpy(result, s1);
    strcat(result, s2);
    return result;
}

/* open perf_event cgroup and initialize the counter by calling perv_event_open */
counter_t init_counters(char * cgroup_name) {
  struct perf_event_attr pe;
  unsigned int nbcores = sysconf(_SC_NPROCESSORS_ONLN);
  memset(&pe, 0, sizeof(struct perf_event_attr));
  pe.size = sizeof(struct perf_event_attr);
  pe.disabled = 1;

  char * filename = concat("/sys/fs/cgroup/perf_event", cgroup_name);
  int fd1 = open(filename, O_RDONLY);
  if (fd1 < 0)
  {
      return NULL;
  }
  printf("Gathering infos for: %s\n", filename);

  counter_t g_counter = malloc(sizeof(counter_t));
  g_counter->nbperf = nb_perf;
  g_counter->nbcores=nbcores;
  g_counter->counters=malloc(nb_perf*sizeof(int*));
  for (int i=0; i<nb_perf; i++) {
    pe.type = perf_type[i];
    pe.config = perf_key[i];
    g_counter->counters[i] = malloc(nbcores*sizeof(int));

    // loop on cores because per-cgroup monitoring is not available with cpu = -1 : https://stackoverflow.com/questions/52892668/using-perf-event-open-to-monitor-docker-containers
    // in cgroup-mode the event is measured only if the thread running on the monitored CPU belongs to the designated cgroup http://man7.org/linux/man-pages/man2/perf_event_open.2.html
    for (int core=0; core<nbcores; core++) {
      g_counter->counters[i][core] = perf_event_open(&pe, fd1, core, -1, PERF_FLAG_PID_CGROUP|PERF_FLAG_FD_CLOEXEC);
    }
  }
  close(fd1);
  free(filename);
  return g_counter;
}

void clean_counters(counter_t g_counter) {
  for(int counter=0; counter<g_counter->nbperf; counter++) {
    for(int core=0; core<g_counter->nbcores; core++)
      close(g_counter->counters[counter][core]);
    free(g_counter->counters[counter]);
  }
  free(g_counter->counters);
  free(g_counter);
}

counter_t start_counters(char *cgroup_name) {
  cgroup_t cgroup = find(cgroup_name);
  counter_t g_counter = NULL;

  if (cgroup == NULL) {
     return NULL;
  } else {
     g_counter = cgroup->g_counter;
  }

  for(int counter=0; counter<g_counter->nbperf; counter++)
    for(int core=0; core<g_counter->nbcores; core++)
      ioctl(g_counter->counters[counter][core], PERF_EVENT_IOC_ENABLE, 0);
  return g_counter;
}

/* reset counters values to 0 */
counter_t reset_counters(counter_t g_counter) {
  for(int counter=0; counter<g_counter->nbperf; counter++)
    for(int core=0; core<g_counter->nbcores; core++)
      ioctl(g_counter->counters[counter][core], PERF_EVENT_IOC_RESET, 0);
  return g_counter;
}

int get_counters(long long *values, char *cgroup_name) {
  cgroup_t cgroup = find(cgroup_name);
  counter_t g_counter = NULL;

  if (cgroup == NULL) {
     return -1;
  } else {
     g_counter = cgroup->g_counter;
  }

  for(int i=0; i<g_counter->nbperf; i++) {
    long long accu=0;
    long long count;
    for (int core=0; core<g_counter->nbcores; core++) {
      if (-1 == read(g_counter->counters[i][core], &count, sizeof(long long))) {
        printf("Error reading counter values \n");
        return -1;
      }
      accu += count;
    }
    values[i] = accu;
  }
  reset_counters(g_counter);
  return 0;
}

// insert the cgroup in the list, init and start its counters
// if the cgroup is already in the list, does nothing
int init_cgroup(char *cgroup_name) {
    cgroup_t cgroup = find(cgroup_name);
    if (cgroup != NULL) {
        return 0;
    } else {
        counter_t g_counter = init_counters(cgroup_name);
        if (g_counter != NULL) {
            insertFirst(cgroup_name, g_counter);
            start_counters(cgroup_name);
            return 0;
        } else {
            return -1;
        }
    }
}

// print linked list of cgroups, used for debugging
void printList() {
   cgroup_t ptr = head;
   printf("[ ");
   while(ptr != NULL) {
      printf("(%s , %d) ",ptr->cgroup_name, ptr->g_counter->nbcores);
      ptr = ptr->next;
   }
   printf(" ] \n");
}

// insert a cgroup at the beginning of the cgroup list
void insertFirst(char *cgroup_name, counter_t g_counter) {
   cgroup_t link = (cgroup_t) malloc(sizeof(cgroup_t));
   link->cgroup_name = strdup(cgroup_name);
   link->g_counter = g_counter;
   link->next = head;
   head = link;
}

// return the cgroup with given name in the list, return NULL if the cgroup is not in the list
cgroup_t find(char *cgroup_name) {
   cgroup_t current = head;
   if(head == NULL) {
      return NULL;
   }
   while (strcmp(current->cgroup_name, cgroup_name) != 0) {
      if(current->next == NULL) {
         return NULL;
      } else {
         current = current->next;
      }
   }
   return current;
}

// clean counters of the cgroup and free the cgroup
void clean_cgroup(cgroup_t cgroup) {
  counter_t g_counter = NULL;
  if (cgroup == NULL) {
     return;
  } else {
     g_counter = cgroup->g_counter;
  }
  free(cgroup->cgroup_name);
  clean_counters(g_counter);
  free(cgroup);
}

// remove from the list the cgroup with given name and free it
void remove_cgroup(char *cgroup_name) {
   cgroup_t current = head;
   cgroup_t previous = NULL;
   if(head == NULL) {
      return;
   }
    while (strcmp(current->cgroup_name, cgroup_name) != 0) {
      if(current->next == NULL) {
         return;
      } else {
         previous = current;
         current = current->next;
      }
   }
   if(current == head) {
      head = head->next;
   } else {
      previous->next = current->next;
   }
   clean_cgroup(current);
}
