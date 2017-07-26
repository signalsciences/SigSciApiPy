# SigSciApiPy
[![Build Status](https://travis-ci.org/signalsciences/SigSciApiPy.svg?branch=master)](https://travis-ci.org/signalsciences/SigSciApiPy)

Sample Signal Sciences Python API Client

### Usage

```
usage: SigSci.py [-h] [--from  =<value>] [--until =<value>]
                 [--tags [TAGS [TAGS ...]]] [--ctags [CTAGS [CTAGS ...]]]
                 [--server SERVER] [--ip IP] [--limit LIMIT]
                 [--field {all,totalCount,next,data}] [--file FILE] [--list]
                 [--format {json,csv}] [--pretty] [--sort {desc,asc}]
                 [--agents] [--feed] [--timeseries] [--rollup ROLLUP]
                 [--list-events] [--event-by-id =<value>]
                 [--whitelist-parameters] [--whitelist-parameters-add]
                 [--whitelist-parameters-delete] [--whitelist-paths]
                 [--whitelist-paths-add] [--whitelist-paths-delete]
                 [--whitelist] [--whitelist-add] [--whitelist-delete]
                 [--blacklist] [--blacklist-add] [--blacklist-delete]
                 [--redactions] [--redactions-add] [--redactions-delete]

Signal Sciences API Client.

optional arguments:
  -h, --help            show this help message and exit
  --from  =<value>      Filter results from a specified time.
  --until =<value>      Filter results until a specified time.
  --tags [TAGS [TAGS ...]]
                        Filter results on one or more tags.
  --ctags [CTAGS [CTAGS ...]]
                        Filter results on one or more custom tags.
  --server SERVER       Filter results by server name.
  --ip IP               Filter results by remote ip.
  --limit LIMIT         Limit the number of results returned from the server
                        (default: 100).
  --field {all,totalCount,next,data}
                        Specify fields to return (default: data).
  --file FILE           Output results to the specified file.
  --list                List all supported tags
  --format {json,csv}   Specify output format (default: json).
  --pretty              Pretty print the JSON ourput.
  --sort {desc,asc}     Specify sort order (default: desc).
  --agents              Retrieve agent metrics.
  --feed                Retrieve data feed.
  --timeseries          Retrieve timeseries data.
  --rollup ROLLUP       Rollup interval in seconds for timeseries requests.
  --list-events         List events (flagged IPs).
  --event-by-id =<value>
                        Get an event by event ID.
  --whitelist-parameters
                        Retrieve whitelist parameters.
  --whitelist-parameters-add
                        Add whitelist parameters.
  --whitelist-parameters-delete
                        Delete whitelist parameters.
  --whitelist-paths     Retrieve whitelist paths.
  --whitelist-paths-add
                        Add whitelist paths.
  --whitelist-paths-delete
                        Delete whitelist paths.
  --whitelist           Retrieve IP whitelist.
  --whitelist-add       Add to IP whitelist.
  --whitelist-delete    Delete IP whitelist.
  --blacklist           Retrieve IP blacklist.
  --blacklist-add       Add to IP blacklist.
  --blacklist-delete    Delete IP blacklist.
  --redactions          Retrieve redactions.
  --redactions-add      Add to redactions.
  --redactions-delete   Delete redactions.
  ```

### Authentication

There are two options for authentication:

__Environment Variables__

```
export SIGSCI_EMAIL=<API User Email>
export SIGSCI_PASSWORD=<API User Password>
export SIGSCI_CORP=<Corp Name>
export SIGSCI_SITE=<Site Name>
```

__Set Variables in Script__

Edit SigSci.py by setting the following variables in the configuration section of the script:

```
...
#### Configuration Section ################
EMAIL    = '' # The email address associated with your
              # Signal Sciences account, e.g. user@yourdomain.com

PASSWORD = '' # The password associated with your Signal Sciences account.

# Your CORP and SITE can be found by logging
# into the Signal Sciences Dashboard. The URL 
# for the overview page contains these values.
# Example:
# https://dashboard.signalsciences.net/<CORP>/<SITE>
#
CORP = ''
SITE = ''
...
```

### Example Usage

Display help.

`./SigSci.py -h`

Return the most recent 100 rows for all tags.

`./SigSci.py`

Return the most recent 1000 rows within the last hour for all tags.

`./SigSci.py --limit 1000 --from =-1h`

Return the most recent 100 rows for specific tags.

`./SigSci.py --tags SQLI XSS TRAVERSAL`

List all valid tags.

`./SigSci.py --list`

Retrieve agent metrics.

`./SigSci.py --agents`

Requests feed (bulk download).

`./SigSci.py --feed`

Retrieve list of events.
`./SigSci.py --list-events`

### Example Module Usage

```
#!/usr/bin/env python
# Retrieve agent metrics and output to file.
#

from SigSciApiPy.SigSci import *
import os.path
import json

# setup sigsci api module
sigsci = SigSciAPI()

# required variables
sigsci.email = ""
sigsci.pword = ""
sigsci.corp  = ""
sigsci.site  = ""
sigsci.file  = "/tmp/sigsci_agent_metrics.json"

# check if temp file already exists, if so then delete it
if os.path.isfile(sigsci.file):
    os.remove(sigsci.file)

if sigsci.authenticate():
    sigsci.get_agent_metrics()

with open(sigsci.file) as json_file:    
    agents = json.load(json_file)

for agent in agents['data']:
    print agent['agent.current_requests']
```
