# SigSciApiPy
Signal Sciences Python API Client

### Usage

```
usage: SigSci.py [-h] [--from  =<value>] [--until =<value>]
                 [--tags [TAGS [TAGS ...]]] [--ctags [CTAGS [CTAGS ...]]]
                 [--server SERVER] [--limit LIMIT]
                 [--field {all,totalCount,next,data}] [--file FILE] [--list]
                 [--format {json,csv}] [--sort {desc,asc}] [--agents] [--feed]
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
  --limit LIMIT         Limit the number of results returned from the server
                        (default: 100).
  --field {all,totalCount,next,data}
                        Specify fields to return (default: data).
  --file FILE           Output results to the specified file.
  --list                List all supported tags
  --format {json,csv}   Specify output format (default: json).
  --sort {desc,asc}     Specify sort order (default: desc).
  --agents              Retrieve agent metrics.
  --feed                Retrieve data feed.
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

### Example Usage

Return the most recent 100 rows for all tags.

`./SigSci.py`

Display help.

`./SigSci.py -h`

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

### Example Module Usage

```
#!/usr/local/bin/python
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
