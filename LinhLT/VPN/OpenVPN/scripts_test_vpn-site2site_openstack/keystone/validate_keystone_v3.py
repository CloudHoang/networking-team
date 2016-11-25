#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
#
# Authors:
#   Duc Nguyen Cong (nguyencongduc3112@gmail.com)
#   Based on: https://github.com/rakesh-patnaik/nagios-openstack-monitoring#
#
# How to use?
# python validate_keystone_v3 --token $keystone_token --auth_url "http://172.16.69.53:5000/v3"

import sys
import argparse
import requests
import json

STATE_OK = 0
STATE_CRITICAL = 2

parser = argparse.ArgumentParser(description='Validate OpenStack Keystone token.')
parser.add_argument('--auth_url', metavar='URL', type=str,
                    required=True,
                    help='Keystone URL')
parser.add_argument('--token', metavar='TOKEN', type=str,
                    required=True,
                    help='The toke need to be validate')
parser.add_argument('--insecure', action='store_false', dest='verify',
                    required=False,
                    help='Disable SSL verification.')
args = parser.parse_args()


headers = {'content-type': 'application/json', 'X-Auth-Token': args.token, 'X-Subject-Token': args.token}


try:

    auth_response = requests.get(args.auth_url + '/auth/tokens', headers=headers, verify=args.verify);

    if auth_response.status_code == 200:
        token = auth_response.json()
        #print "Authentication success. "
        #print "Token is validated for user %s, project %s, domain %s untill %s" \
          #      %(token['token']['user']['name'], token['token']['project']['name'], \
          #     token['token']['project']['domain']['name'], token['token']['expires_at'].split('.')[0])
        sys.exit(STATE_OK)
    else:
        #print 'CRITICAL: Failed to validate token' 
        #print auth_response.json()['error']['message']
        sys.exit(STATE_CRITICAL)

except Exception as e:
    #print 'CRITICAL: Athentication failed!'
    sys.exit(STATE_CRITICAL)
