# baseline

_Use Meraki Systems Manager to baseline apps against a source machine_

---

This python program leverages APIs to the Meraki dashboard to get a list of software installed on a source computer and compare that to other computers in the same network. Output lists apps that should be added or removed to meet the baseline.

## Features

* Progress bar because the querying the dashboard can be slow
* No error checking. Get your command line options right 
* API key can be specified via environment variable, CLI, or variable

## Solution Components

This app leverages the following APIs and packages:
 * meraki v1.38.0 for access to the dashboard
 * plac v1.4 for CLI option parsing
 * alive-progress v3.1.4 for progress bar

### Cisco Products / Services

* This uses the Meraki Dashboard and a Systems Manager network

## Usage

usage: baseline.py [-h] [-v] [-a APIKEY] [-n NET] [-e EXCLUSIONS]
                   source [targets ...]

Identify applications that need to be installed or removed from a baseline computer

positional arguments:
&emsp;source                Source PC
&emsp;targets               Zero or more targets

options:
&emsp;-h, --help            show this help message and exit
&emsp;-v, --verbose         Enable verbose mode
&emsp;-a APIKEY, --apikey APIKEY
                        Dashboard API KEY
&emsp;-n NET, --net NET     Network ID
&emsp;-e EXCLUSIONS, --exclusions EXCLUSIONS
                        Filename of exclusions

## Installation

Required packages can be installed with pip install -r requirements.txt
