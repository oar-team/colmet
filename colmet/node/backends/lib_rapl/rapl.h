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
void clean_rapl(rapl_t rapl);
int get_rapl_size();

extern rapl_t g_rapl;
