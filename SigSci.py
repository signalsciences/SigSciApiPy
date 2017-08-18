#!/usr/bin/env python

"""
Signal Sciences Python API Client
"""

from __future__ import print_function
import argparse
import csv
import datetime
import json
import os
import sys
from builtins import str

import requests

# Configuration Section ###################

# The email address associated with your
# Signal Sciences account, e.g. user@yourdomain.com
EMAIL = ''

# The password associated with your Signal Sciences account.
PASSWORD = ''

# Your CORP and SITE can be found by logging
# into the Signal Sciences Dashboard. The URL
# for the overview page contains these values.
# Example:
# https://dashboard.signalsciences.net/<CORP>/<SITE>
#
CORP = ''
SITE = ''

# API Query settings
# For help with time search syntax see:
# https://dashboard.signalsciences.net/documentation/knowledge-base/search-syntax#time
FROM = None  # example: FROM = '-6h'
UNTIL = None  # example: UNTIL = '-4h'
TAGS = None  # example: TAGS = 'SQLI XSS TRAVERSAL'
CTAGS = None  # example: CTAGS = 'bad-bot failed-login'
SERVER = None  # example: SERVER = 'example.com'
IP = None  # example: IP = '66.228.162.36'
LIMIT = None  # example: LIMIT = 250
FIELD = None  # example: FIELD = 'all'
FILE = None  # example: FILE = '/tmp/sigsci.json'
FORMAT = None  # example: FORMAT = 'csv'
PRETTY = None  # PRETTY = true
SORT = None  # example: SORT = 'asc'
###########################################

# default for retrieving agent metrics
AGENTS = False
# default for feed requests
FEED = False
# default for timeseries
TIMESERIES = False
ROLLUP = 60
# list events
LIST_EVENTS = False
EVENT_BY_ID = None
# default for custom alerts
CUSTOM_ALERTS = False
CUSTOM_ALERTS_ADD = False
CUSTOM_ALERTS_DELETE = False
# default for whitelist parameters
WHITELIST_PARAMETERS = False
WHITELIST_PARAMETERS_ADD = False
WHITELIST_PARAMETERS_DELETE = False
# default for whitelist paths
WHITELIST_PATHS = False
WHITELIST_PATHS_ADD = False
WHITELIST_PATHS_DELETE = False
# default for whitelist
WHITELIST = False
WHITELIST_ADD = False
WHITELIST_DELETE = False
# default for blacklist
BLACKLIST = False
BLACKLIST_ADD = False
BLACKLIST_DELETE = False
# default for redactions
REDACTIONS = False
REDACTIONS_ADD = False
REDACTIONS_DELETE = False
###########################################

sys.dont_write_bytecode = True


class SigSciAPI(object):
    """
    SigSciAPI()
    Methods:
        authenticate()
        build_query(from_time=<string>, until_time=<string>, tags=<list>)
        query_api()

    Example:
        sigsci       = SigSciAPI()
        sigsci.email = 'foo@bar.com'
        sigsci.pword = 'c0mpl3x'
        sigsci.corp  = 'foo_bar'
        sigsci.site  = 'www.bar.com'
        sigsci.limit = 1000
        sigsci.file  = '/tmp/foo.json'

        if sigsci.authenticate():
            sigsci.build_query(from_time='-6h', until_time='-5h', tags=['SQLI', 'XSS', 'CMDEXE'])
            sigsci.query_api()
    """
    base = 'https://dashboard.signalsciences.net'
    url = base + '/api/'
    version = 'v0'
    base_url = None
    authn = None
    token = None
    email = None
    pword = None
    corp = None
    site = None
    query = 'from:-6h '
    from_time = '-1h'
    until_time = None
    tags = None
    ctags = None
    server = None
    ip = None
    limit = 100
    field = 'data'
    file = None
    format = 'json'
    pretty = False
    sort = 'desc'
    agent_ver = '0.0.1'
    ua = 'Signal Sciences Client API (Python/{})'.format(agent_ver)
    xheaders = {}
    event_by_id = None

    # api end points
    LOGIN_EP = '/auth'
    LOGOUT_EP = '/auth/logout'
    CORPS_EP = '/corps/'
    SITES_EP = '/sites/'
    MEMBERS_EP = '/members'
    USERS_EP = '/users'
    REQEUSTS_EP = '/requests'
    AGENTS_EP = '/agents'
    FEED_EP = '/feed/requests'
    ALERTS_EP = '/alerts'
    RULES_EP = '/rules'
    TAGS_EP = '/tags'
    TIMESERIES_EP = '/timeseries/requests'
    EVENTS_EP = '/events'
    WLPARAMS_EP = '/paramwhitelist'
    WLPATHS_EP = '/pathwhitelist'
    WHITELIST_EP = '/whitelist'
    BLACKLIST_EP = '/blacklist'
    REDACTIONS_EP = '/redactions'
    INTEGRATIONS_EP = '/integrations'
    CONFIGURED_TEMPLATES_EP = '/configuredtemplates'

    def authenticate(self):
        """
        SigSciAPI.authenticate()

        Before calling, set:
            SigSciAPI.email
            SigSciAPI.pword

        Stores auth token in:
            SigSciAPI.authn.token
        """

        self.authn = requests.post(self.base_url + self.LOGIN_EP,
                                   data={'email': self.email, 'password': self.pword},
                                   allow_redirects=False)

        if self.authn.status_code == 401:
            print(self.authn.json()['message'])
            return False
        elif self.authn.status_code == 403:
            print(self.authn.json()['message'])
            return False
        elif self.authn.status_code != 200:
            print('Unexpected status: %s response: %s' % (self.authn.status_code, self.authn.text))
            return False

        self.token = self.authn.json()['token']
        return True

    def get_headers(self):
        headers = {'Content-type': 'application/json', 'User-Agent': self.ua}

        if self.token is not None:
            headers['Authorization'] = 'Bearer %s' % self.token

        if self.xheaders:
            headers.update(self.xheaders)

        return headers

    def set_headers(self, headers):
        self.xheaders.update(headers)

    def build_query(self):
        """
        SigSciAPI.build_query()

        For from_time and until_time syntax see:
        https://dashboard.signalsciences.net/documentation/knowledge-base/search-syntax#time

        Default values (query):
            SigSciAPI.from_time  = -1h
            SigSciAPI.until_time = None
            SigSciAPI.tags       = <all tags>
        """

        if self.from_time is not None:
            self.query = 'from:%s ' % str(self.from_time)

        if self.until_time is not None:
            self.query += 'until:%s ' % str(self.until_time)

        if self.server is not None:
            self.query += 'server:%s ' % str(self.server)

        if self.ip is not None:
            self.query += 'ip:%s ' % str(self.ip)

        if self.sort is not None:
            self.query += 'sort:time-%s ' % str(self.sort)

        if self.tags is not None:
            self.query += 'tag:'
            self.query += ' tag:'.join(self.tags)
            self.query += ' '  # extra space required for appending ctags

        if self.ctags is not None:
            self.query += 'tag:'
            self.query += ' tag:'.join(self.ctags)

    def query_api(self):
        """
        SigSciAPI.query_api()

        Before calling, set:
            (Required):
                SigSciAPI.corp
                SigSciAPI.site

            (Optional):
                SigSciAPI.query
                SigSciAPI.limit
                SigSciAPI.file

        """

        try:
            url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.REQEUSTS_EP + '?q=' + str(self.query).strip() + '&limit=' + str(self.limit)
            r = requests.get(url, cookies=self.authn.cookies, headers=self.get_headers())
            j = json.loads(r.text)
            f = None if self.field == 'all' else self.field

            if 'message' in j:
                raise ValueError(j['message'])

            if self.format == 'json':
                if not self.file:
                    if f is None:
                        print('%s' % json.dumps(j))
                        self.json_out(j)
                    else:
                        print('%s' % json.dumps(j[f]))
                else:
                    with open(self.file, 'a') as outfile:
                        if f is None:
                            outfile.write('%s' % json.dumps(j))
                        else:
                            outfile.write('%s' % json.dumps(j[f]))

            elif self.format == 'csv':
                if not self.file:
                    csvwritter = csv.writer(sys.stdout)
                else:
                    csvwritter = csv.writer(open(self.file, "wb+"))

                # for now only output data "j['data']"
                f = None
                if f is None:
                    for row in j['data']:
                        tag_list = ''
                        detector = row['tags']

                        for t in detector:
                            tag_list = tag_list + t['type'] + '|'

                        csvwritter.writerow([str(row['timestamp']), str(row['id']), str(row['remoteIP']), str(row['remoteCountryCode']), str(row['path']).encode('utf8'), str(tag_list[:-1]), str(row['responseCode']), str(row['agentResponseCode'])])
                else:
                    print('%s' % json.dumps(j[f]))

            else:
                print('Error: Invalid output format!')

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)

    def get_feed_requests(self):
        """
        SigSciAPI.get_feed_requests()

        Before calling, set:
            (Required):
                SigSciAPI.corp
                SigSciAPI.site

            (Optional):
                SigSciAPI.from_time
                SigSciAPI.until_time
                SigSciAPI.tags
                SigSciAPI.file
                SigSciAPI.format

        """
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__feed_requests_get
        # /corps/{corpName}/sites/{siteName}/feed/requests
        try:
            now = datetime.datetime.now()

            if self.from_time is None:
                tm = now - datetime.timedelta(hours=1, minutes=5)
                stm = tm.strftime("%Y-%m-%d %H:%M:00")
                self.from_time = int(tm.strptime(stm, "%Y-%m-%d %H:%M:00").strftime("%s"))
                self.query = 'from=%s' % str(self.from_time)
            else:
                self.query = 'from=%s' % str(self.from_time)

            if self.until_time is None:
                tm = now - datetime.timedelta(minutes=5)
                stm = tm.strftime("%Y-%m-%d %H:%M:00")
                self.until_time = int(tm.strptime(stm, "%Y-%m-%d %H:%M:00").strftime("%s"))
                self.query += '&until=%s' % str(self.until_time)
            else:
                self.query += '&until=%s' % str(self.until_time)

            if self.tags is not None:
                self.query += '&tags='
                self.query += ','.join(self.tags)

            if self.ctags is not None:
                if self.tags is None:
                    self.query += '&tags='

                self.query += ','.join(self.ctags)

            url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.FEED_EP + '?' + str(self.query).strip()
            r = requests.get(url, cookies=self.authn.cookies, headers=self.get_headers())
            j = json.loads(r.text)

            if 'message' in j:
                raise ValueError(j['message'])

            if self.format == 'json':
                if not self.file:
                    print('%s' % json.dumps(j['data']))

                else:
                    with open(self.file, 'a') as outfile:
                        outfile.write('%s' % json.dumps(j['data']))

            # get all next
            next_ref = j['next']
            while next_ref['uri'].strip() != '':
                url = self.base + next_ref['uri']
                r = requests.get(url, headers=self.get_headers())
                j = json.loads(r.text)

                if 'message' in j:
                    raise ValueError(j['message'])

                if self.format == 'json':
                    if not self.file:
                        print('%s' % json.dumps(j['data']))

                    else:
                        with open(self.file, 'a') as outfile:
                            outfile.write('%s' % json.dumps(j['data']))

                next_ref = j['next']

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)

    def get_timeseries(self, tag, rollup=60):
        """
        SigSciAPI.get_timeseries(tag, rollup)

        Before calling, set:
            (Required):
                SigSciAPI.corp
                SigSciAPI.site
                SigSciAPI.tags

            (Optional):
                SigSciAPI.from_time
                SigSciAPI.until_time
                SigSciAPI.file
                SigSciAPI.format

        """
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__timeseries_requests_get
        # /corps/{corpName}/sites/{siteName}/timeseries/requests

        try:
            self.query = '?tag=%s&rollup=%s' % (str(tag).strip(), str(rollup).strip())

            if self.from_time is not None:
                self.query += '&from=%s' % str(self.from_time)

            if self.until_time is not None:
                self.query += '&until=%s' % str(self.until_time)

            url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.TIMESERIES_EP + self.query
            r = requests.get(url, cookies=self.authn.cookies, headers=self.get_headers())
            j = json.loads(r.text)

            self.json_out(j)

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()

    def get_list_events(self, tag=None):
        """
        SigSciAPI.get_list_events(tag)

        Before calling, set:
            (Required):
                SigSciAPI.corp
                SigSciAPI.site

            (Optional):
                SigSciAPI.tags
                SigSciAPI.from_time
                SigSciAPI.until_time
                SigSciAPI.file
                SigSciAPI.format

        """
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__events_get
        # /corps/{corpName}/sites/{siteName}/events
        try:
            query_params = '?limit=' + str(self.limit)

            if tag is not None:
                query_params += '&tag=%s' % (str(tag).strip())

            url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.EVENTS_EP + query_params
            r = requests.get(url, cookies=self.authn.cookies, headers=self.get_headers())
            j = json.loads(r.text)

            self.json_out(j)

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()

    def get_event_by_id(self):
        """
        SigSciAPI.get_event_by_id()

        Before calling, set:
            (Required):
                SigSciAPI.corp
                SigSciAPI.site
                SigSciAPI.event_id

            (Optional):
                SigSciAPI.file
                SigSciAPI.format

        """
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__events__eventID__get
        # /corps/{corpName}/sites/{siteName}/events/{eventID}
        try:
            url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.EVENTS_EP + '/' + self.event_by_id
            r = requests.get(url, cookies=self.authn.cookies, headers=self.get_headers())
            j = json.loads(r.text)

            self.json_out(j)

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()

    def get_list(self, url):
        try:
            r = requests.get(url, cookies=self.authn.cookies, headers=self.get_headers())
            j = json.loads(r.text)

            self.json_out(j)

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()

    def get_agent_metrics(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__agents_get
        # /corps/{corpName}/sites/{siteName}/agents
        url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.AGENTS_EP
        return self.get_list(url)

    def get_agent_logs(self, agent_name):
        # https://docs.signalsciences.net/api/#_corps__corpName__sites__siteName__agents__agentName__logs_get
        # /corps/{corpName}/sites/{siteName}/agents/{agentName}/logs

        try:
            url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.AGENTS_EP + '/' + agent_name + '/logs'
            r = requests.get(url, cookies=self.authn.cookies, headers=self.get_headers())
            j = json.loads(r.text)

            self.json_out(j)

        except Exception as e:
            print('Error: %s ' % str(e))
            quit()

    def get_corps(self):
        if self.corp is None:
            url = self.base_url + self.CORPS_EP[:-1]
        else:
            url = self.base_url + self.CORPS_EP + self.corp

        return self.get_list(url)

    def get_sites(self):
        url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP[:-1]
        return self.get_list(url)

    def get_members(self):
        url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + self.MEMBERS_EP
        return self.get_list(url)

    def get_users(self):
        url = self.base_url + self.CORPS_EP + self.corp + self.USERS_EP
        return self.get_list(url)

    def get_configuration(self, EP):
        try:
            url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + EP
            r = requests.get(url, cookies=self.authn.cookies, headers=self.get_headers())
            j = json.loads(r.text)

            self.json_out(j)

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()

    def post_configuration(self, EP):
        try:
            url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + EP

            with open(self.file) as data_file:
                data = json.load(data_file)

            for config in data['data']:
                if 'created' in config:
                    del config['created']

                if 'createdBy' in config:
                    del config['createdBy']

                if 'id' in config:
                    del config['id']

                if EP == self.TAGS_EP and 'tagName' in config:
                    del config['tagName']

                r = requests.post(url, cookies=self.authn.cookies, headers=self.get_headers(), json=config)
                j = json.loads(r.text)

                if 'message' in j:
                    print('Data: %s ' % json.dumps(config))
                    raise ValueError(j['message'])

            print("Post complete!")

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()

    def delete_configuration(self, EP):
        try:
            url = self.base_url + self.CORPS_EP + self.corp + self.SITES_EP + self.site + EP

            with open(self.file) as data_file:
                data = json.load(data_file)

            for config in data['data']:
                url = url + "/" + config['id']
                requests.delete(url, cookies=self.authn.cookies, headers=self.get_headers())

            print("Delete complete!")

        except Exception as e:
            print('Error: %s ' % str(e))
            print('Query: %s ' % url)
            quit()

    def get_custom_alerts(self):
        # https://docs.signalsciences.net/api/#_corps__corpName__sites__siteName__alerts_get
        # /corps/{corpName}/sites/{siteName}/alerts
        self.get_configuration(self.ALERTS_EP)

    def post_custom_alerts(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__rules_post
        # /corps/{corpName}/sites/{siteName}/alerts
        self.post_configuration(self.ALERTS_EP)

    def delete_custom_alerts(self):
        # https://docs.signalsciences.net/api/#_corps__corpName__sites__siteName__alerts__alertID__delete
        # /corps/{corpName}/sites/{siteName}/alerts/{alertID}
        self.delete_configuration(self.ALERTS_EP)

    def get_custom_rules(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__rules_get
        # /corps/{corpName}/sites/{siteName}/rules
        self.get_configuration(self.RULES_EP)

    def post_custom_rules(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__rules_post
        # /corps/{corpName}/sites/{siteName}/rules
        self.post_configuration(self.RULES_EP)

    def delete_custom_rules(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__rules__ruleID__delete
        # /corps/{corpName}/sites/{siteName}/rules/{ruleID}
        self.delete_configuration(self.RULES_EP)
    
    def get_custom_tags(self):
        # WARNING: This is an undocumented endpoint. No support provided, and the endpoint may change.
        # /corps/{corpName}/sites/{siteName}/tags
        self.get_configuration(self.TAGS_EP)

    def post_custom_tags(self):
        # WARNING: This is an undocumented endpoint. No support provided, and the endpoint may change.
        # /corps/{corpName}/sites/{siteName}/tags
        self.post_configuration(self.TAGS_EP)

    def delete_custom_tags(self):
        # WARNING: This is an undocumented endpoint. No support provided, and the endpoint may change.
        # /corps/{corpName}/sites/{siteName}/tags/{tagID}
        self.delete_configuration(self.TAGS_EP)

    def get_configured_templates(self):
        # WARNING: This is an undocumented endpoint. No support provided, and the endpoint may change.
        self.get_configuration(self.CONFIGURED_TEMPLATES_EP)

    def get_whitelist_parameters(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__paramwhitelist_get
        # /corps/{corpName}/sites/{siteName}/paramwhitelist
        self.get_configuration(self.WLPARAMS_EP)

    def post_whitelist_parameters(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__paramwhitelist_post
        # /corps/{corpName}/sites/{siteName}/paramwhitelist
        self.post_configuration(self.WLPARAMS_EP)

    def delete_whitelist_parameters(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__paramwhitelist__paramID__delete
        # /corps/{corpName}/sites/{siteName}/paramwhitelist/{paramID}
        self.delete_configuration(self.WLPARAMS_EP)

    def get_whitelist_paths(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathwhitelist_get
        # /corps/{corpName}/sites/{siteName}/pathwhitelist
        self.get_configuration(self.WLPATHS_EP)

    def post_whitelist_paths(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathwhitelist_post
        # /corps/{corpName}/sites/{siteName}/pathwhitelist
        self.post_configuration(self.WLPATHS_EP)

    def delete_whitelist_paths(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathwhitelist__pathID__delete
        # /corps/{corpName}/sites/{siteName}/pathwhitelist/{pathID}
        self.delete_configuration(self.WLPATHS_EP)

    def get_whitelist(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__whitelist_get
        # /corps/{corpName}/sites/{siteName}/whitelist
        self.get_configuration(self.WHITELIST_EP)

    def post_whitelist(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathwhitelist_post
        # /corps/{corpName}/sites/{siteName}/whitelist
        self.post_configuration(self.WHITELIST_EP)

    def delete_whitelist(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathwhitelist__pathID__delete
        # /corps/{corpName}/sites/{siteName}/whitelist/{source}
        self.delete_configuration(self.WHITELIST_EP)

    def get_blacklist(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__blacklist_get
        # /corps/{corpName}/sites/{siteName}/blacklist
        self.get_configuration(self.BLACKLIST_EP)

    def post_blacklist(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathblacklist_post
        # /corps/{corpName}/sites/{siteName}/blacklist
        self.post_configuration(self.BLACKLIST_EP)

    def delete_blacklist(self):
        # https://dashboard.signalsciences.net/documentation/api#_corps__corpName__sites__siteName__pathblacklist__pathID__delete
        # /corps/{corpName}/sites/{siteName}/blacklist/{source}
        self.delete_configuration(self.BLACKLIST_EP)

    def get_redactions(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__redactions_get
        # /corps/{corpName}/sites/{siteName}/redactions
        self.get_configuration(self.REDACTIONS_EP)

    def post_redactions(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__redactions_post
        # /corps/{corpName}/sites/{siteName}/redactions
        self.post_configuration(self.REDACTIONS_EP)

    def delete_redactions(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__redactions__field__delete
        # /corps/{corpName}/sites/{siteName}/redactions/{field}
        self.delete_configuration(self.REDACTIONS_EP)

    def get_integrations(self):
        # https://dashboard.signalsciences-stage.net/documentation/api#_corps__corpName__sites__siteName__redactions_get
        # /corps/{corpName}/sites/{siteName}/redactions
        self.get_configuration(self.INTEGRATIONS_EP)

    def json_out(self, j):
        if 'message' in j:
            raise ValueError(j['message'])

        if self.format == 'json':
            if not self.file:
                if self.pretty:
                    print('%s' % json.dumps(j, sort_keys=True, indent=4, separators=(',', ': ')))
                else:
                    print('%s' % json.dumps(j))

            else:
                with open(self.file, 'a') as outfile:
                    outfile.write('%s' % json.dumps(j))

        elif self.format == 'csv':
            print("CSV output not available for this request.")

    def __init__(self):
        self.base_url = self.url + self.version


if __name__ == '__main__':
    TAGLIST = ('SQLI', 'XSS', 'CMDEXE', 'TRAVERSAL', 'USERAGENT', 'BACKDOOR', 'SCANNER', 'RESPONSESPLIT', 'CODEINJECTION',
               'HTTP4XX', 'HTTP404', 'HTTP500', 'SANS', 'DATACENTER', 'TORNODE', 'NOUA', 'NOTUTF8', 'BLOCKED', 'PRIVATEFILES', 'FORCEFULBROWSING', 'WEAKTLS')

    parser = argparse.ArgumentParser(description='Signal Sciences API Client.', prefix_chars='--')

    parser.add_argument('--from', help='Filter results from a specified time.', dest='from_time', metavar=' =<value>', type=str, default=None)
    parser.add_argument('--until', help='Filter results until a specified time.', dest='until_time', metavar='=<value>')
    parser.add_argument('--tags', help='Filter results on one or more tags.', nargs='*')
    parser.add_argument('--ctags', help='Filter results on one or more custom tags.', nargs='*')
    parser.add_argument('--server', help='Filter results by server name.', default=None)
    parser.add_argument('--ip', help='Filter results by remote ip.', default=None)
    parser.add_argument('--limit', help='Limit the number of results returned from the server (default: 100).', type=int, default=100)
    parser.add_argument('--field', help='Specify fields to return (default: data).', type=str, default=None, choices=['all', 'totalCount', 'next', 'data'])
    parser.add_argument('--file', help='Output results to the specified file.', type=str, default=None)
    parser.add_argument('--list', help='List all supported tags', default=False, action='store_true')
    parser.add_argument('--format', help='Specify output format (default: json).', type=str, default='json', choices=['json', 'csv'])
    parser.add_argument('--pretty', help='Pretty print the JSON ourput.', default=False, action='store_true')
    parser.add_argument('--sort', help='Specify sort order (default: desc).', type=str, default=None, choices=['desc', 'asc'])
    parser.add_argument('--agents', help='Retrieve agent metrics.', default=False, action='store_true')
    parser.add_argument('--feed', help='Retrieve data feed.', default=False, action='store_true')
    parser.add_argument('--timeseries', help='Retrieve timeseries data.', default=False, action='store_true')
    parser.add_argument('--rollup', help='Rollup interval in seconds for timeseries requests.', default=60)
    parser.add_argument('--list-events', help='List events (flagged IPs).', default=False, action='store_true')
    parser.add_argument('--event-by-id', help='Get an event by event ID.', type=str, default=None, dest='event_by_id', metavar='=<value>')
    parser.add_argument('--custom-alerts', help='Retrieve custom alerts.', default=False, action='store_true')
    parser.add_argument('--custom-alerts-add', help='Add custom alerts.', default=False, action='store_true')
    parser.add_argument('--custom-alerts-delete', help='Delete custom alerts.', default=False, action='store_true')
    parser.add_argument('--whitelist-parameters', help='Retrieve whitelist parameters.', default=False, action='store_true')
    parser.add_argument('--whitelist-parameters-add', help='Add whitelist parameters.', default=False, action='store_true')
    parser.add_argument('--whitelist-parameters-delete', help='Delete whitelist parameters.', default=False, action='store_true')
    parser.add_argument('--whitelist-paths', help='Retrieve whitelist paths.', default=False, action='store_true')
    parser.add_argument('--whitelist-paths-add', help='Add whitelist paths.', default=False, action='store_true')
    parser.add_argument('--whitelist-paths-delete', help='Delete whitelist paths.', default=False, action='store_true')
    parser.add_argument('--whitelist', help='Retrieve IP whitelist.', default=False, action='store_true')
    parser.add_argument('--whitelist-add', help='Add to IP whitelist.', default=False, action='store_true')
    parser.add_argument('--whitelist-delete', help='Delete IP whitelist.', default=False, action='store_true')
    parser.add_argument('--blacklist', help='Retrieve IP blacklist.', default=False, action='store_true')
    parser.add_argument('--blacklist-add', help='Add to IP blacklist.', default=False, action='store_true')
    parser.add_argument('--blacklist-delete', help='Delete IP blacklist.', default=False, action='store_true')
    parser.add_argument('--redactions', help='Retrieve redactions.', default=False, action='store_true')
    parser.add_argument('--redactions-add', help='Add to redactions.', default=False, action='store_true')
    parser.add_argument('--redactions-delete', help='Delete redactions.', default=False, action='store_true')

    arguments = parser.parse_args()

    # list supported tags and quit
    if arguments.list:
        print('Supported tags:')
        for tag in TAGLIST:
            print('\t%s' % str(tag))

        quit()

    # setup and run api query
    sigsci = SigSciAPI()

    # first get configuration, environment variables (if set) override
    # settings specified at the beginning of this script.
    sigsci.email = os.environ.get('SIGSCI_EMAIL') if os.environ.get('SIGSCI_EMAIL') is not None else EMAIL
    sigsci.pword = os.environ.get("SIGSCI_PASSWORD") if os.environ.get('SIGSCI_PASSWORD') is not None else PASSWORD
    sigsci.corp = os.environ.get("SIGSCI_CORP") if os.environ.get('SIGSCI_CORP') is not None else CORP
    sigsci.site = os.environ.get("SIGSCI_SITE") if os.environ.get('SIGSCI_SITE') is not None else SITE
    sigsci.from_time = os.environ.get("SIGSCI_FROM") if os.environ.get('SIGSCI_FROM') is not None else FROM
    sigsci.until_time = os.environ.get("SIGSCI_UNTIL") if os.environ.get('SIGSCI_UNTIL') is not None else UNTIL
    sigsci.tags = os.environ.get("SIGSCI_TAGS") if os.environ.get('SIGSCI_TAGS') is not None else TAGS
    sigsci.ctags = os.environ.get("SIGSCI_CTAGS") if os.environ.get('SIGSCI_CTAGS') is not None else CTAGS
    sigsci.server = os.environ.get("SIGSCI_SERVER") if os.environ.get('SIGSCI_SERVER') is not None else SERVER
    sigsci.ip = os.environ.get("SIGSCI_IP") if os.environ.get('SIGSCI_IP') is not None else IP
    sigsci.limit = os.environ.get("SIGSCI_LIMIT") if os.environ.get('SIGSCI_LIMIT') is not None else LIMIT
    sigsci.field = os.environ.get("SIGSCI_FIELD") if os.environ.get('SIGSCI_FIELD') is not None else FIELD
    sigsci.file = os.environ.get("SIGSCI_FILE") if os.environ.get('SIGSCI_FILE') is not None else FILE
    sigsci.format = os.environ.get("SIGSCI_FORMAT") if os.environ.get('SIGSCI_FORMAT') is not None else FORMAT
    sigsci.pretty = os.environ.get("SIGSCI_PRETTY") if os.environ.get('SIGSCI_PRETTY') is not None else PRETTY
    sigsci.sort = os.environ.get("SIGSCI_SORT") if os.environ.get('SIGSCI_SORT') is not None else SORT
    sigsci.agents = os.environ.get("SIGSCI_AGENTS") if os.environ.get('SIGSCI_AGENTS') is not None else AGENTS
    sigsci.feed = os.environ.get("SIGSCI_FEED") if os.environ.get('SIGSCI_FEED') is not None else FEED
    sigsci.timeseries = os.environ.get("SIGSCI_TIMESERIES") if os.environ.get('SIGSCI_TIMESERIES') is not None else TIMESERIES
    sigsci.rollup = os.environ.get("SIGSCI_ROLLUP") if os.environ.get('SIGSCI_ROLLUP') is not None else ROLLUP
    sigsci.list_events = os.environ.get("SIGSCI_LIST_EVENTS") if os.environ.get('SIGSCI_LIST_EVENTS') is not None else LIST_EVENTS
    sigsci.event_by_id = os.environ.get("SIGSCI_EVENT_BY_ID") if os.environ.get('SIGSCI_EVENT_BY_ID') is not None else EVENT_BY_ID
    sigsci.custom_alerts = os.environ.get("SIGSCI_CUSTOM_ALERTS") if os.environ.get('SIGSCI_CUSTOM_ALERTS') is not None else CUSTOM_ALERTS
    sigsci.custom_alerts_add = os.environ.get("SIGSCI_CUSTOM_ALERTS_ADD") if os.environ.get('SIGSCI_CUSTOM_ALERTS_ADD') is not None else CUSTOM_ALERTS_ADD
    sigsci.custom_alerts_delete = os.environ.get("SIGSCI_CUSTOM_ALERTS_DELETE") if os.environ.get('SIGSCI_CUSTOM_ALERTS_DELETE') is not None else CUSTOM_ALERTS_DELETE
    sigsci.whitelist_parameters = os.environ.get("SIGSCI_WHITELIST_PARAMETERS") if os.environ.get('SIGSCI_WHITELIST_PARAMETERS') is not None else WHITELIST_PARAMETERS
    sigsci.whitelist_parameters_add = os.environ.get("SIGSCI_WHITELIST_PARAMETERS_ADD") if os.environ.get('SIGSCI_WHITELIST_PARAMETERS_ADD') is not None else WHITELIST_PARAMETERS_ADD
    sigsci.whitelist_parameters_delete = os.environ.get("SIGSCI_WHITELIST_PARAMETERS_DELETE") if os.environ.get('SIGSCI_WHITELIST_PARAMETERS_DELETE') is not None else WHITELIST_PARAMETERS_DELETE
    sigsci.whitelist_paths = os.environ.get("SIGSCI_WHITELIST_PATHS") if os.environ.get('SIGSCI_WHITELIST_PATHS') is not None else WHITELIST_PATHS
    sigsci.whitelist_paths_add = os.environ.get("SIGSCI_WHITELIST_PATHS_ADD") if os.environ.get('SIGSCI_WHITELIST_PATHS_ADD') is not None else WHITELIST_PATHS_ADD
    sigsci.whitelist_paths_delete = os.environ.get("SIGSCI_WHITELIST_PATHS_DELETE") if os.environ.get('SIGSCI_WHITELIST_PATHS_DELETE') is not None else WHITELIST_PATHS_DELETE
    sigsci.whitelist = os.environ.get("SIGSCI_WHITELIST") if os.environ.get('SIGSCI_WHITELIST') is not None else WHITELIST
    sigsci.whitelist_add = os.environ.get("SIGSCI_WHITELIST_ADD") if os.environ.get('SIGSCI_WHITELIST_ADD') is not None else WHITELIST_ADD
    sigsci.whitelist_delete = os.environ.get("SIGSCI_WHITELIST_DELETE") if os.environ.get('SIGSCI_WHITELIST_DELETE') is not None else WHITELIST_DELETE
    sigsci.blacklist = os.environ.get("SIGSCI_BLACKLIST") if os.environ.get('SIGSCI_BLACKLIST') is not None else BLACKLIST
    sigsci.blacklist_add = os.environ.get("SIGSCI_BLACKLIST_ADD") if os.environ.get('SIGSCI_BLACKLIST_ADD') is not None else BLACKLIST_ADD
    sigsci.blacklist_delete = os.environ.get("SIGSCI_BLACKLIST_DELETE") if os.environ.get('SIGSCI_BLACKLIST_DELETE') is not None else BLACKLIST_DELETE
    sigsci.redactions = os.environ.get("SIGSCI_REDACTIONS") if os.environ.get('SIGSCI_REDACTIONS') is not None else REDACTIONS
    sigsci.redactions_add = os.environ.get("SIGSCI_REDACTIONS_ADD") if os.environ.get('SIGSCI_REDACTIONS_ADD') is not None else REDACTIONS_ADD
    sigsci.redactions_delete = os.environ.get("SIGSCI_REDACTIONS_DELETE") if os.environ.get('SIGSCI_REDACTIONS_DELETE') is not None else REDACTIONS_DELETE

    # if command line arguments exist then override any previously set values.
    # note: there is no command line argument for EMAIL, PASSWORD, CORP, or SITE.
    sigsci.from_time = arguments.from_time if arguments.from_time is not None else sigsci.from_time
    sigsci.until_time = arguments.until_time if arguments.until_time is not None else sigsci.until_time
    sigsci.tags = arguments.tags if arguments.tags is not None else sigsci.tags
    sigsci.ctags = arguments.ctags if arguments.ctags is not None else sigsci.ctags
    sigsci.server = arguments.server if arguments.server is not None else sigsci.server
    sigsci.ip = arguments.ip if arguments.ip is not None else sigsci.ip
    sigsci.limit = arguments.limit if arguments.limit is not None else sigsci.limit
    sigsci.field = arguments.field if arguments.field is not None else sigsci.field
    sigsci.file = arguments.file if arguments.file is not None else sigsci.file
    sigsci.format = arguments.format if arguments.format is not None else sigsci.format
    sigsci.pretty = arguments.pretty if arguments.pretty is not None else sigsci.pretty
    sigsci.sort = arguments.sort if arguments.sort is not None else sigsci.sort
    sigsci.agents = arguments.agents if arguments.agents is not None else sigsci.agents
    sigsci.feed = arguments.feed if arguments.feed is not None else sigsci.feed
    sigsci.timeseries = arguments.timeseries if arguments.timeseries is not None else sigsci.timeseries
    sigsci.rollup = arguments.rollup if arguments.rollup is not None else sigsci.rollup
    sigsci.list_events = arguments.list_events if arguments.list_events is not None else sigsci.list_events
    sigsci.event_by_id = arguments.event_by_id if arguments.event_by_id is not None else sigsci.event_by_id
    sigsci.custom_alerts = arguments.custom_alerts if arguments.custom_alerts is not None else sigsci.custom_alerts
    sigsci.custom_alerts_add = arguments.custom_alerts_add if arguments.custom_alerts_add is not None else sigsci.custom_alerts_add
    sigsci.custom_alerts_delete = arguments.custom_alerts_delete if arguments.custom_alerts_delete is not None else sigsci.custom_alerts_delete
    sigsci.whitelist_parameters = arguments.whitelist_parameters if arguments.whitelist_parameters is not None else sigsci.whitelist_parameters
    sigsci.whitelist_parameters_add = arguments.whitelist_parameters_add if arguments.whitelist_parameters_add is not None else sigsci.whitelist_parameters_add
    sigsci.whitelist_parameters_delete = arguments.whitelist_parameters_delete if arguments.whitelist_parameters_delete is not None else sigsci.whitelist_parameters_delete
    sigsci.whitelist_paths = arguments.whitelist_paths if arguments.whitelist_paths is not None else sigsci.whitelist_paths
    sigsci.whitelist_paths_add = arguments.whitelist_paths_add if arguments.whitelist_paths_add is not None else sigsci.whitelist_paths_add
    sigsci.whitelist_paths_delete = arguments.whitelist_paths_delete if arguments.whitelist_paths_delete is not None else sigsci.whitelist_paths_delete
    sigsci.whitelist = arguments.whitelist if arguments.whitelist is not None else sigsci.whitelist
    sigsci.whitelist_add = arguments.whitelist_add if arguments.whitelist_add is not None else sigsci.whitelist_add
    sigsci.whitelist_delete = arguments.whitelist_delete if arguments.whitelist_delete is not None else sigsci.whitelist_delete
    sigsci.blacklist = arguments.blacklist if arguments.blacklist is not None else sigsci.blacklist
    sigsci.blacklist_add = arguments.blacklist_add if arguments.blacklist_add is not None else sigsci.blacklist_add
    sigsci.blacklist_delete = arguments.blacklist_delete if arguments.blacklist_delete is not None else sigsci.blacklist_delete
    sigsci.redactions = arguments.redactions if arguments.redactions is not None else sigsci.redactions
    sigsci.redactions_add = arguments.redactions_add if arguments.redactions_add is not None else sigsci.redactions_add
    sigsci.redactions_delete = arguments.redactions_delete if arguments.redactions_delete is not None else sigsci.redactions_delete

    # authenticate before doing anything.
    if sigsci.authenticate():

        # determine what we are doing.
        if sigsci.agents:
            # get agent metrics
            sigsci.get_agent_metrics()

        elif sigsci.feed:
            # get feed
            sigsci.get_feed_requests()

        elif sigsci.timeseries:
            # get timeseries data
            if sigsci.tags is not None:
                for tag in sigsci.tags:
                    sigsci.get_timeseries(tag, sigsci.rollup)

        elif sigsci.list_events:
            # get event data
            if sigsci.tags is not None:
                for tag in sigsci.tags:
                    sigsci.get_list_events(tag.upper())
            else:
                sigsci.get_list_events()

        elif sigsci.event_by_id is not None:
            # get event data
            sigsci.get_event_by_id()

        elif sigsci.custom_alerts:
            # get custom alerts
            sigsci.get_custom_alerts()

        elif sigsci.custom_alerts_add:
            # post whitelist parameters
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_custom_alerts()

        elif sigsci.custom_alerts_delete:
            # delete whitelist parameters
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_custom_alerts()

        elif sigsci.whitelist_parameters:
            # get whitelist parameters
            sigsci.get_whitelist_parameters()

        elif sigsci.whitelist_parameters_add:
            # post whitelist parameters
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_whitelist_parameters()

        elif sigsci.whitelist_parameters_delete:
            # delete whitelist parameters
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_whitelist_parameters()

        elif sigsci.whitelist_paths:
            # get whitelist paths
            sigsci.get_whitelist_paths()

        elif sigsci.whitelist_paths_add:
            # post whitelist paths
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_whitelist_paths()

        elif sigsci.whitelist_paths_delete:
            # delete whitelist paths
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_whitelist_paths()

        elif sigsci.whitelist:
            # get ip whitelist
            sigsci.get_whitelist()

        elif sigsci.whitelist_add:
            # post ip whitelist
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_whitelist()

        elif sigsci.whitelist_delete:
            # delete ip whitelist
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_whitelist()

        elif sigsci.blacklist:
            # get ip blacklist
            sigsci.get_blacklist()

        elif sigsci.blacklist_add:
            # post ip blacklist
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_blacklist()

        elif sigsci.blacklist_delete:
            # delete ip blacklist
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_blacklist()

        elif sigsci.redactions:
            # get redactions
            sigsci.get_redactions()

        elif sigsci.redactions_add:
            # post redactions
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.post_redactions()

        elif sigsci.redactions_delete:
            # delete redactions
            if not sigsci.file:
                print('File must be provided.')
                quit()
            else:
                sigsci.delete_redactions()

        else:
            # verify provided tags are supported tags
            if sigsci.tags is not None:
                for tag in sigsci.tags:
                    if not set([tag.upper()]).issubset(set(TAGLIST)):
                        print('Invalid tag in tag list: %s' % str(tag))
                        quit()

            # build the query, and run the query.
            sigsci.build_query()
            sigsci.query_api()
