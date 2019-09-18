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
  int **perf_indexes;
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

// name : metric name in natural language
// perf_type : type of event associated with the metric (field type of perf_event_attr struct)
// perf_key : metric name (field config of perf_event_attr struct)
typedef struct counter_option {
  char *name;
  __u32 perf_type;
  __u64 perf_key;
} counter_option;

// metrics that can be collected using perf_event_open
// they were obtained using the parsing script counters_option.py from mojito/s https://sourcesup.renater.fr/www/mojitos/
static counter_option perf_static_info[] = {
{ .name = "cpu_cycles", .perf_type = PERF_TYPE_HARDWARE, .perf_key = PERF_COUNT_HW_CPU_CYCLES},
{ .name = "instructions", .perf_type = PERF_TYPE_HARDWARE, .perf_key = PERF_COUNT_HW_INSTRUCTIONS},
{ .name = "cache_references", .perf_type = PERF_TYPE_HARDWARE, .perf_key = PERF_COUNT_HW_CACHE_REFERENCES},
{ .name = "cache_misses", .perf_type = PERF_TYPE_HARDWARE, .perf_key = PERF_COUNT_HW_CACHE_MISSES},
{ .name = "branch_instructions", .perf_type = PERF_TYPE_HARDWARE, .perf_key = PERF_COUNT_HW_BRANCH_INSTRUCTIONS},
{ .name = "branch_misses", .perf_type = PERF_TYPE_HARDWARE, .perf_key = PERF_COUNT_HW_BRANCH_MISSES},
{ .name = "bus_cycles", .perf_type = PERF_TYPE_HARDWARE, .perf_key = PERF_COUNT_HW_BUS_CYCLES},
{ .name = "ref_cpu_cycles", .perf_type = PERF_TYPE_HARDWARE, .perf_key = PERF_COUNT_HW_REF_CPU_CYCLES},
{ .name = "cache_l1d", .perf_type = PERF_TYPE_HW_CACHE, .perf_key = PERF_COUNT_HW_CACHE_L1D},
{ .name = "cache_ll", .perf_type = PERF_TYPE_HW_CACHE, .perf_key = PERF_COUNT_HW_CACHE_LL},
{ .name = "cache_dtlb", .perf_type = PERF_TYPE_HW_CACHE, .perf_key = PERF_COUNT_HW_CACHE_DTLB},
{ .name = "cache_itlb", .perf_type = PERF_TYPE_HW_CACHE, .perf_key = PERF_COUNT_HW_CACHE_ITLB},
{ .name = "cache_bpu", .perf_type = PERF_TYPE_HW_CACHE, .perf_key = PERF_COUNT_HW_CACHE_BPU},
{ .name = "cache_node", .perf_type = PERF_TYPE_HW_CACHE, .perf_key = PERF_COUNT_HW_CACHE_NODE},
{ .name = "cache_op_read", .perf_type = PERF_TYPE_HW_CACHE, .perf_key = PERF_COUNT_HW_CACHE_OP_READ},
{ .name = "cache_op_prefetch", .perf_type = PERF_TYPE_HW_CACHE, .perf_key = PERF_COUNT_HW_CACHE_OP_PREFETCH},
{ .name = "cache_result_access", .perf_type = PERF_TYPE_HW_CACHE, .perf_key = PERF_COUNT_HW_CACHE_RESULT_ACCESS},
{ .name = "cpu_clock", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_CPU_CLOCK},
{ .name = "task_clock", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_TASK_CLOCK},
{ .name = "page_faults", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_PAGE_FAULTS},
{ .name = "context_switches", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_CONTEXT_SWITCHES},
{ .name = "cpu_migrations", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_CPU_MIGRATIONS},
{ .name = "page_faults_min", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_PAGE_FAULTS_MIN},
{ .name = "page_faults_maj", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_PAGE_FAULTS_MAJ},
{ .name = "alignment_faults", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_ALIGNMENT_FAULTS},
{ .name = "emulation_faults", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_EMULATION_FAULTS},
{ .name = "dummy", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_DUMMY},
{ .name = "bpf_output", .perf_type = PERF_TYPE_SOFTWARE, .perf_key = PERF_COUNT_SW_BPF_OUTPUT},
};

static unsigned int nb_counter_option = 28;

int nb_perf = 5;
int* perf_indexes=NULL;

// parse a string containing metric names in natural language (ex : "instruction,cpu_cycles,cache_misses") and fill perf_indexes with the corresponding indexes of perf_static_info
void perf_event_list(char *perf_string, int *nb_perf, int **perf_indexes) {
  char *token;
  *nb_perf=0;
  *perf_indexes=NULL;
  while((token=strtok(perf_string, ",")) != NULL) {
    perf_string = NULL;
    int i;
    for(i=0; i<nb_counter_option; i++) {
      if(strcmp(perf_static_info[i].name, token) == 0) {
	(*nb_perf)++;
	(*perf_indexes) = realloc(*perf_indexes, sizeof(int)*(*nb_perf));
	(*perf_indexes)[*nb_perf-1]=i;
	break;
      }
    }
    if(i == nb_counter_option) {
      fprintf(stdout, "Unknown performance counter: %s\n", token);
      fflush(stdout);
//      exit(EXIT_FAILURE);
    }
  }
}


static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
		int cpu, int group_fd, unsigned long flags) {
  long res = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);

  if (res == -1) {
    fprintf(stdout, "Error opening leader %llx %d\n", hw_event->config, errno);
    fflush(stdout);
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
counter_t init_counters(char *cgroup_name, int *perf_indexes) {
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
  fflush(stdout);

  counter_t g_counter = malloc(sizeof(counter_t));
  g_counter->nbperf = nb_perf;
  g_counter->nbcores=nbcores;
  g_counter->counters=malloc(nb_perf*sizeof(int*));
  for (int i=0; i<nb_perf; i++) {
    int index = perf_indexes[i];
    pe.type = perf_static_info[index].perf_type;
    pe.config = perf_static_info[index].perf_key;
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
        fflush(stdout);
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
int init_cgroup(char *cgroup_name, char *metrics) {

    printf("Cgroup name received %s \n", cgroup_name);
    fflush(stdout);
    printf("Metrics received : %s \n", metrics);
    fflush(stdout);
    cgroup_t cgroup = find(cgroup_name);
    if (cgroup != NULL) {
        return 1;
    } else {
        char *metrics_copy = strdup(metrics);
        perf_event_list(metrics_copy, &nb_perf, &perf_indexes);
	printf("metric_copy : %s \n", metrics_copy);
	fflush(stdout);
	printf("nb_perf : %d \n", nb_perf);
	fflush(stdout);
	printf("perf_indexes[0] : %d \n", perf_indexes[0]);
	fflush(stdout);
        free(metrics_copy);
        counter_t g_counter = init_counters(cgroup_name, perf_indexes);
        if (g_counter != NULL) {
            insertFirst(cgroup_name, g_counter);
            start_counters(cgroup_name);
            return 2;
        } else {
            return 3;
        }
    }
}

// print linked list of cgroups, used for debugging
void printList() {
   cgroup_t ptr = head;
   printf("[ ");
   while(ptr != NULL) {
      printf("(%s , %d, %d) ",ptr->cgroup_name, ptr->g_counter->nbcores, ptr->g_counter->nbperf);
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

//void main(){
//    char options[] = "page_faults,instructions,cache_node,instructions,instructions";
//    init_cgroup("/oar/lrocher_1876192", options);
//    char options2[] = "instructions,page_faults,cache_node";
//    init_cgroup("/oar/lrocher_2", options2);
//
//
//    long long *counters1 = malloc(sizeof(long long)*3);
//    long long *counters2 = malloc(sizeof(long long)*3);
//
//    get_counters(counters1, "/oar/lrocher_1876192");
//    get_counters(counters2, "/oar/lrocher_2");
//
//    printList();
//    printf("ok");
//}
