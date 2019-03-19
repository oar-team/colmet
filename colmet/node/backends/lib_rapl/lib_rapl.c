/*******************************************************
 * Copyright (C) 2018 Georges Da Costa <georges.da-costa@irit.fr>
 *******************************************************/

#include <stdio.h>
#include <stdlib.h>
#include "rapl.h"

#define MAX_LEN_NAME 100

const int nbzones = 3;
const int rapl_zones[3] = { POWERCAP_RAPL_ZONE_PACKAGE,   POWERCAP_RAPL_ZONE_CORE,   POWERCAP_RAPL_ZONE_DRAM};

rapl_t g_rapl;

int init_rapl() {
  g_rapl = malloc(sizeof(struct _rapl_t));

  // get number of processor sockets

  g_rapl->nbpackages = powercap_rapl_get_num_packages();
  if (g_rapl->nbpackages == 0) {
    //no packages found
    return -1;
  }

  g_rapl->pkgs = malloc(g_rapl->nbpackages * sizeof(powercap_rapl_pkg));
  for (int package = 0; package < g_rapl->nbpackages; package++)
    if (powercap_rapl_init(package, &g_rapl->pkgs[package], 0)) {
      return -1;
    }

  g_rapl->names = malloc(sizeof(char*)* g_rapl->nbzones*g_rapl->nbpackages);
  for (int package = 0; package < g_rapl->nbpackages; package++) {
    for(int zone=0; zone<g_rapl->nbzones; zone++) {
     g_rapl->names[package*g_rapl->nbzones+zone]=malloc(MAX_LEN_NAME);
      powercap_rapl_get_name(&g_rapl->pkgs[package], rapl_zones[zone], g_rapl->names[package*g_rapl->nbzones+zone], MAX_LEN_NAME);
    }
  }
  return 0;
}

int get_rapl_size(){
  return g_rapl->nbpackages * g_rapl->nbzones;
}


void clean_rapl(rapl_t rapl) {
  for (int package = 0; package < rapl->nbpackages; package++) {
    if (powercap_rapl_destroy(&rapl->pkgs[package]))
      perror("powercap_rapl_destroy");
    for (int zone=0; zone<rapl->nbzones; zone++)
      free(rapl->names[package*rapl->nbzones+zone]);
  }
  free(rapl->names);
  free(rapl->pkgs);
  free(rapl);
}

