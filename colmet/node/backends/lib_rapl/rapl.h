/*******************************************************
 * Copyright (C) 2018 Georges Da Costa <georges.da-costa@irit.fr>
 *******************************************************/

#include <powercap/powercap-rapl.h>

struct _rapl_t {
  powercap_rapl_pkg* pkgs;
  uint32_t nbpackages;
  uint32_t nbzones;
  char **names;
  const int* zones;
};

typedef struct _rapl_t* rapl_t;

int init_rapl();
int clean_rapl();
int get_rapl_size();

/**
 * Get the max energy range in microjoules.
 */
void get_powercap_rapl_get_max_energy_range_uj(uint64_t* val);

/**
 * Get the current energy in microjoules.
 */
void get_powercap_rapl_get_energy_uj(uint64_t* val);

void get_powercap_rapl_name(char ** values);

extern rapl_t g_rapl;
