#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from fabric.api import task, run, local, lcd, env, cd, sudo, execute, hosts
import fabtools

env.use_ssh_config = True
env.roledefs = {
    'dev': ['localhost'],
}

if not env.roles:
    env.roles = ['dev']


@task
def system_packages():
    """ Install required system packages. """
    fabtools.deb.update_index(quiet=False)
    fabtools.require.deb.packages([
        'python-zmq',
        'python-tables',
        'python-h5py',
        'python-pyinotify',
    ])


@task(alias="venv")
def deploy():
    """ Deploy colmet. """
    execute(system_packages)
    sudo("python setup.py install")
