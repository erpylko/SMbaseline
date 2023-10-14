#!/usr/bin/env python3

"""
Copyright (c) 2023 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

#
# an app to return all the programs on a Meraki Systems Manager network
#
# you need an API key as well as network ID for a systems manager network
# 
import meraki
import plac
from alive_progress import alive_it
import os
import time

#
# The API key and network ID can be used multiple ways.
#
#   - specified as environment variable
#   - specified on cli
#   - specified in app
#
# That list is least relevant to most relevant. If both an environment
# variable is set and the API_KEY variable is set, the program will use
# the locally set variable
#
#API_KEY = ''
#NET_ID  = ''

# not verbose output by default
VERBOSE = False

# default exclusions file
EXCLUSIONS='exclusions.txt'

#
# only print things if quiet has not been set
#
def vprint(text):
    if VERBOSE:
        print(text)

#
# read in the app names to exclude from the report.
#
# default file exclusions.txt is loaded if it exists.
# that is overridden by the CLI option
# 
# file has one app name/line
#
def loadExclusions(textfile):
    if textfile is None:
        if os.path.isfile(EXCLUSIONS):
            vprint("Loading default exclusions")
            fn = EXCLUSIONS
        else:
            # no exclusions, return an empty set
            return(set())
    else:
        if os.path.isfile(textfile):
            fn = textfile
        else:
            print("Exclusions file does not exist. Exiting.")
            exit()

    appList = set()

    ignore = open(fn, 'r')

    for app in ignore:
        appList.add(app.strip())

    ignore.close()

    if len(appList) == 0:
        vprint("No exclusions found")

    return (appList)

#
# API keys and network IDs can be specified through environment variables,
# global variables, or the CLI. Most specific to least specific is:
# CLI -> Global Variable -> environment variable
#
def setKey(key):
    g = globals()
  
    if key in g:
        return g[key]
    else:
        return os.environ.get(key)

#
# extract the software names from a Meraki dashboard object. Return as a set
#
def extractSoftware(softwares):
    pcsw = set()

    for software in softwares:
        swname = software['name']
        pcsw.add(swname)

    return (pcsw)


#
# command line options/descriptions
#
@plac.flg('verbose',   'Enable verbose mode')
@plac.opt('apikey',    'Dashboard API KEY',      type=str)
@plac.opt('net',       'Network ID',             type=str)
@plac.opt('exclusions','Filename of exclusions', type=str)
@plac.pos('source',    'Source PC',              type=str)
@plac.pos('targets',   'Zero or more targets',   type=str, metavar='targets')
def main(verbose, apikey, net, exclusions, source, *targets):
    """Identify applications that need to be installed or removed from a baseline computer"""

    global VERBOSE # need access to the global scope
    
    if verbose:
        VERBOSE=True
   
    if apikey is None:
        apikey = setKey('API_KEY')

    if apikey is None:
        print("Need to set APIKEY. Exiting.")
        exit ()

    if net is None:
        net = setKey('NET_ID')

    if net is None:
        print("Need to set NET_ID. Exiting.")
        exit ()

    excluded=loadExclusions(exclusions)

    # create dashboard object
    vprint("Connecting to Meraki Dashboard...")
    dashboard = meraki.DashboardAPI(apikey, output_log=False, suppress_logging=True)
  
    # get a list of all devices
    vprint("Gathering devices...")
    device_list = dashboard.sm.getNetworkSmDevices(net)

    target_names=set()
    target_ids={}
    target_sw={}

    for device in device_list:
        name = device['name'].upper().strip()
        id = device['id']
        target_names.add(name)
        target_ids[name] = id
        vprint(id+" "+name)

    # make sure the source device exists
    source = source.upper()
    if (source not in target_names):
        print("Can't find source in Meraki Dashboard. Exiting.")
        exit()
    else:
        vprint("Getting source software")
        target_sw[source] = extractSoftware(dashboard.sm.getNetworkSmDeviceSoftwares(net, target_ids[source]))-excluded
        # don't need the source name to be processed in targets now
        target_names.remove(source)

    tlen = len(targets)
    t = set()
    
    if tlen != 0:
        for target in targets:
            target = target.upper()
            if (target in target_names):
                t.add(target.upper().strip())
        if len(t) == 0:
            print("No specified targets found. Exiting.")
            exit()
        else:
            target_names = t
    else:
        vprint("No targets specified. Baselining ALL computers.")

    # iterate through all devices, build the list of all software in the net
    for device in alive_it(target_names, length=25, title='Processing PC', disable=verbose):
        # get the installed software for a host
        target_sw[device]=extractSoftware(dashboard.sm.getNetworkSmDeviceSoftwares(net, target_ids[device]))-excluded

    # use set math to easily remove apps that we don't want to see (if any)

    for device in sorted(target_names):
        missing = target_sw[source] - target_sw[device]
        extra = target_sw[device] - target_sw[source]
        print("Apps to install on",device)
        for m in missing:
            print(" +",m)
        print("Apps to remove from",device)
        for e in extra:
            print(" -",e)
    pass

if __name__ == '__main__':
    plac.call(main)

