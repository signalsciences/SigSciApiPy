# SigSciApiPy
[![Build Status](https://travis-ci.org/signalsciences/SigSciApiPy.svg?branch=master)](https://travis-ci.org/signalsciences/SigSciApiPy)

Sample Signal Sciences Python API Client

This script can be used on the command line to query the Signal Sciences API, or it can be included as a module to query the API in your own Python script.

## :rotating_light: NOTICE :rotating_light:

Effective **May 17th 2021** the default branch will change from `master` to `main`. Run the following commands to update a local clone:
```
git branch -m master main
git fetch origin
git branch -u origin/main main
git remote set-head origin -a
```

### Command Line Options

```
usage: SigSci.py [-h] [--from  =<value>] [--until =<value>]
                 [--tags [TAGS [TAGS ...]]] [--ctags [CTAGS [CTAGS ...]]]
                 [--server SERVER] [--ip IP] [--limit LIMIT]
                 [--field {all,totalCount,next,data}] [--file FILE] [--list]
                 [--format {json,csv}] [--pretty] [--sort {desc,asc}]
                 [--agents] [--feed] [--feed2] [--timeseries]
                 [--rollup ROLLUP] [--list-events] [--event-by-id =<value>]
                 [--custom-alerts] [--custom-alerts-add]
                 [--custom-alerts-delete] [--whitelist-parameters]
                 [--whitelist-parameters-add] [--whitelist-parameters-delete]
                 [--whitelist-paths] [--whitelist-paths-add]
                 [--whitelist-paths-delete] [--whitelist] [--whitelist-add]
                 [--whitelist-delete] [--blacklist] [--blacklist-add]
                 [--blacklist-delete] [--request-rules] [--request-rules-add]
                 [--request-rules-delete] [--signal-rules]
                 [--signal-rules-add] [--signal-rules-delete] [--redactions]
                 [--redactions-add] [--redactions-delete] [--integrations]
                 [--headerlinks] [--version]

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
                        (max: 999).
  --field {all,totalCount,next,data}
                        Specify fields to return (default: data).
  --file FILE           Output results to the specified file.
  --list                List all supported tags
  --format {json,csv}   Specify output format (default: json).
  --pretty              Pretty print the JSON ourput.
  --sort {desc,asc}     Specify sort order (default: asc).
  --agents              Retrieve agent metrics.
  --feed                Retrieve data feed.
  --feed2               Retrieve data feed. Version 2
  --timeseries          Retrieve timeseries data.
  --rollup ROLLUP       Rollup interval in seconds for timeseries requests.
  --list-events         List events (flagged IPs).
  --event-by-id =<value>
                        Get an event by event ID.
  --custom-alerts       Retrieve custom alerts.
  --custom-alerts-add   Add custom alerts.
  --custom-alerts-delete
                        Delete custom alerts.
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
  --request-rules       Retrieve request rules.
  --request-rules-add   Add request rules.
  --request-rules-delete
                        Delete request rules.
  --signal-rules        Retrieve signal rules.
  --signal-rules-add    Add signal rules.
  --signal-rules-delete
                        Delete signal rules.
  --redactions          Retrieve redactions.
  --redactions-add      Add to redactions.
  --redactions-delete   Delete redactions.
  --integrations        Retrieve integrations.
  --headerlinks         Retrieve headerlinks.
  --version             Display version.
  ```

### Authentication

There are several options for specifying your credentials for authentication. You can set credentials via environment variables or via a configuration file. In addition, you can use API tokens (preferred) or password.

Note: If you set values for both API token and password, API token will take precedence.

#### Authenticate Using Environment Variables (with API token)

```
export SIGSCI_EMAIL=<API User Email>
export SIGSCI_API_TOKEN=<API Token>
export SIGSCI_CORP=<Corp Name>
export SIGSCI_SITE=<Site Name>
```

#### Authenticate Using Environment Variables (without API token)

```
export SIGSCI_EMAIL=<API User Email>
export SIGSCI_PASSWORD=<API User Password>
export SIGSCI_CORP=<Corp Name>
export SIGSCI_SITE=<Site Name>
```

#### Authenticate Using Configuration File

You can specify a configuration file with the `--config` option. See [example configuration file](example.conf).

### With API token

```
[sigsci]
email=<API User Email>
api-token =<API Token>
corp=<Corp Name>
site=<Site Name>
```

### Without API token

```
[sigsci]
email=<API User Email>
password=<API User Password>
corp=<Corp Name>
site=<Site Name>
```

### Example Command Line Usage

Display help.

`./SigSci.py -h`

Return all requests that have been tagged in the last 6 hours.

`./SigSci.py`

Return all requests that have been tagged in the last 6 hours in CSV format.

`./SigSci.py --format csv`

Return all requests that have been tagged in the last hour in CSV format.

`./SigSci.py --format csv --from=-1h`

Return all requests that have been tagged with SQLI, XSS, or TRAVERSAL starting at 4 hours ago until 2 hours ago.

`./SigSci.py --from=-4h --until=-2h --tags SQLI XSS TRAVERSAL`

Retrieve agent metrics.

`./SigSci.py --agents`

Requests feed (bulk download).

`./SigSci.py --feed`

Retrieve list of events.

`./SigSci.py --list-events`

Copying configurations from one site to another.

```
export SIGSCI_EMAIL=<API User Email>
export SIGSCI_PASSWORD=<API User Password>
export SIGSCI_CORP=<Corp Name>

# Site name that has the config you wish to copy:
export SIGSCI_SITE=<Source Site Name>

./SigSci.py —-custom-alerts —-file source-config.json

# Change site variable to the site you wish to copy config to:
export SIGSCI_SITE=<Target Site Name>

./SigSci.py —-custom-alerts-add —-file source-config.json

rm source-config.json
```

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
