#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import htpc
from urllib import quote
from urllib2 import urlopen, Request
from json import loads
import logging
import base64
from cherrypy.lib.auth2 import require
from jsonrpclib import jsonrpc


class NZBGet:
    def __init__(self):
        self.logger = logging.getLogger('modules.nzbget')
        htpc.MODULES.append({
            'name': 'NZBGet',
            'id': 'nzbget',
            'test': htpc.WEBDIR + 'nzbget/version',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'nzbget_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'nzbget_name'},
                {'type': 'text', 'label': 'IP / Host', 'placeholder':'localhost', 'name': 'nzbget_host'},
                {'type': 'text', 'label': 'Port', 'placeholder':'6789', 'name': 'nzbget_port'},
                {'type': 'text', 'label': 'Basepath', 'placeholder':'/nzbget', 'name': 'nzbget_basepath'},
                {'type': 'text', 'label': 'User', 'name': 'nzbget_username'},
                {'type': 'password', 'label': 'Password', 'name': 'nzbget_password'},
                {'type': 'bool', 'label': 'Use SSL', 'name': 'nzbget_ssl'}
        ]})

    @cherrypy.expose()
    @require()
    def index(self):
        return htpc.LOOKUP.get_template('nzbget.html').render(scriptname='nzbget')

    @cherrypy.expose()
    @require()
    def nzbget_url(self):
        host = htpc.settings.get('nzbget_host', '')
        port = str(htpc.settings.get('nzbget_port', ''))
        username = htpc.settings.get('nzbget_username', '')
        password = htpc.settings.get('nzbget_password', '')
        nzbget_basepath = htpc.settings.get('nzbget_basepath', '/')
        ssl = 's' if htpc.settings.get('nzbget_ssl', True) else ''

        if(nzbget_basepath == ""):
            nzbget_basepath = "/"
        if not(nzbget_basepath.endswith('/')):
            nzbget_basepath += "/"
        if username and  password:
            authstring = '%s:%s@' % (username, password)
        else:
            authstring = ''

        url = 'http' + ssl + '://' + authstring + host + ':' + port + nzbget_basepath + 'jsonrpc/'
        print url
        return url


    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def version(self, nzbget_host, nzbget_basepath, nzbget_port, nzbget_username, nzbget_password, nzbget_ssl=False, **kwargs):
        self.logger.debug("Fetching version information from nzbget")
        ssl = 's' if nzbget_ssl else ''

        if(nzbget_basepath == ""):
            nzbget_basepath = "/"
        if not(nzbget_basepath.endswith('/')):
            nzbget_basepath += "/"

        url = 'http' + ssl + '://'+  nzbget_host + ':' + nzbget_port + nzbget_basepath + 'jsonrpc/version'
        try:
            request = Request(url)
            if(nzbget_username != ""):
                base64string = base64.encodestring(nzbget_username + ':' + nzbget_password).replace('\n', '')
                request.add_header("Authorization", "Basic %s" % base64string)
            self.logger.debug("Fetching information from: " + url)
            return loads(urlopen(request, timeout=10).read())
        except:
            self.logger.error("Unable to contact nzbget via " + url)
            return

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetHistory(self, limit=''):
        self.logger.debug("Fetching history")
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
        #return self.fetch('history')
        #return nzbget.listgroups()
        return nzbget.history()

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def AddNzb(self, nzb_url= ''):
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
        nzb = urlopen(nzb_url).read()
        #status = nzbget.append('test', '', False, base64.encode(nzb))
        nzbget.append('tempname', '', False, base64.standard_b64encode(nzb))

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetConfig(self):
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
        return nzbget.config()


    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetWarnings(self):
        self.logger.debug("Fetching warnings")
        #array log(int IDFrom, int NumberOfEntries)
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
        return nzbget.log(0, 1000)
        #return self.fetch('log?NumberOfEntries=1000&IDFrom=0')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def queue(self):
        self.logger.debug("Fetching queue")
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
        #return self.fetch('listgroups')
        return nzbget.listgroups()

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def status(self):
        self.logger.debug("Fetching nzbget status")
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
        return nzbget.status()
        #return self.fetch('status')

    def fetch(self, path):
        try:
            host = htpc.settings.get('nzbget_host', '')
            port = str(htpc.settings.get('nzbget_port', ''))
            username = htpc.settings.get('nzbget_username', '')
            password = htpc.settings.get('nzbget_password', '')
            nzbget_basepath = htpc.settings.get('nzbget_basepath', '/')
            ssl = 's' if htpc.settings.get('nzbget_ssl', True) else ''

            if(nzbget_basepath == ""):
                nzbget_basepath = "/"
            if not(nzbget_basepath.endswith('/')):
                nzbget_basepath += "/"

            url = 'http' + ssl + '://' + host + ':' + port + nzbget_basepath + 'jsonrpc/' + path
            request = Request(url)
            base64string = base64.encodestring(username + ':' + password).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
            self.logger.debug("Fetching information from: " + url)
            return loads(urlopen(request, timeout=10).read())
        except:
            self.logger.error("Cannot contact nzbget via: " + url)
            return
