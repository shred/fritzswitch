#!/usr/bin/env python3
#
# fritzswitch - Switch your Fritz!DECT200 via command line
#
# Copyright (C) 2014 Richard "Shred" Körber
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import hashlib
from urllib.request import urlopen
from xml.etree.ElementTree import parse

class FritzHomeAuto:
    def __init__(self, user, password, url):
        """Create a connection to the Fritz!Box with the given user and password."""
        self.fritzurl = url
        self.sid = self.get_sid(user, password)

    def get_sid(self, user, password):
        """Authenticate and get a Session ID"""
        with urlopen(self.fritzurl + '/login_sid.lua') as f:
            dom = parse(f)
            sid = dom.findtext('./SID')
            challenge = dom.findtext('./Challenge')
            
        if sid == '0000000000000000':
            md5 = hashlib.md5()
            md5.update(challenge.encode('utf-16le'))
            md5.update('-'.encode('utf-16le'))
            md5.update(password.encode('utf-16le'))
            response = challenge + '-' + md5.hexdigest()
            uri = self.fritzurl + '/login_sid.lua?username=' + user + '&response=' + response
            with urlopen(uri) as f:
                dom = parse(f)
                sid = dom.findtext('./SID')

        if sid == '0000000000000000':
            raise PermissionError('access denied')

        return sid
        
    def execute(self, cmd, ain=None):
        """Execute a command."""
        if ain:
            uri = self.fritzurl + '/webservices/homeautoswitch.lua?ain=' + ain + '&switchcmd=' + cmd + '&sid=' + self.sid
        else:
            uri = self.fritzurl + '/webservices/homeautoswitch.lua?switchcmd=' + cmd + '&sid=' + self.sid
        return urlopen(uri)
        
    def fetch_string(self, cmd, ain=None):
        """Execute a command and get the result as single-lined string."""
        with self.execute(cmd, ain) as f:
            result = f.read()
        return result.decode().strip()

    def fetch_bool(self, cmd, ain=None):
        """Execute a command and get the result as boolean value."""
        val = self.fetch_string(cmd, ain)
        if val != 'inval':
            return val == '1'
        else:
            return None

    def fetch_int(self, cmd, ain=None):
        """Execute a command and get the result as integer value."""
        val = self.fetch_string(cmd, ain)
        if val != 'inval':
            return int(val)
        else:
            return None

    def get_switch_list(self):
        """Get a dict of all defined switches (ain and name)."""
        ains = {}
        with self.execute('getswitchlist') as f:
            for line in f.readlines():
                ain = line.decode().strip()
                name = self.get_switch_name(ain)
                ains[ain] = name
        return ains
            
    def get_switch_name(self, ain):
        """Get the name of a switch."""
        return self.fetch_string('getswitchname', ain)
    
    def switch(self, ain, mode):
        """Change the switch, turning it 'on', 'off' or 'toggle' it."""
        return self.fetch_bool('setswitch' + mode, ain)
        
    def get_state(self, ain):
        """Get the current state of the switch."""
        result = {}
        result['present'] = self.fetch_bool('getswitchpresent', ain)
        result['name'] = self.get_switch_name(ain)
        if result['present']:
            result['state'] = self.fetch_bool('getswitchstate', ain)
            
            power = self.fetch_int('getswitchpower', ain)
            if power:
                result['power'] = ('%.2f W' % (power / 1000))
                
            result['energy'] = ('%d Wh' % (self.fetch_int('getswitchenergy', ain)))
        return result



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FritzBox Home Automation')
    parser.add_argument('-u', '--user', default='admin', help='User name')
    parser.add_argument('-p', '--password', required=True, help='Password')
    parser.add_argument('-H', '--host', default='fritz.box', help='FritzBox base URL')
    parser.add_argument('-l', '--list', action='store_true', help='List available AIDs')
    parser.add_argument('-a', '--ain', help='AIN')
    parser.add_argument('-0', '--off', dest='switch', action='store_const', const='off', help='Turn AIN off')
    parser.add_argument('-1', '--on', dest='switch', action='store_const', const='on', help='Turn AIN on')
    parser.add_argument('-t', '--toggle', dest='switch', action='store_const', const='toggle', help='Toggle AIN')
    parser.add_argument('-s', '--state', action='store_true', help='Get state of AIN')
    args = parser.parse_args()
    
    host = args.host
    if not (host.startswith('http://') and host.startswith('https://')):
        host = 'http://' + host
    if host.endswith('/'):
        host = host[0:-1]
    
    fha = FritzHomeAuto(args.user, args.password, host)
    
    if args.ain and args.switch:
        mode = fha.switch(args.ain, args.switch)
        if mode:
            print('%s is now on' % (args.ain))
        else:
            print('%s is now off' % (args.ain))
            
    elif args.ain and args.state:
        state = fha.get_state(args.ain)
        for key in sorted(state):
            print('%-10s : %s' % (key, state[key]))
    
    elif args.list:
        switches = fha.get_switch_list()
        for ain in switches:
            print('%s : %s' % (ain, switches[ain]))

