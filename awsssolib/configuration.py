#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: awsssolib.py
#
# Copyright 2020 Sayantan Khanra
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for awsssolib.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

SUPPORTED_TARGETS = ['GetUserPoolInfo',
                     'SearchGroups',
                     'ProvisionApplicationInstanceForAWSAccount',
                     'ListPermissionSets',
                     'GetApplicationInstanceForAWSAccount',
                     'ProvisionApplicationProfileForAWSAccountInstance',
                     'AssociateProfile',
                     'ListAWSAccountProfiles',
                     'DisassociateProfile',
                     'SearchUsers',
                     'ListMembersInGroup',
                     'ListGroupsForUser',
                     'CreatePermissionSet',
                     'PutPermissionsPolicy',
                     'GetPermissionsPolicy',
                     'ListAccountsWithProvisionedPermissionSet',
                     'UpdatePermissionSet']

DEFAULT_AWS_REGION = 'eu-west-1'
API_CONTENT_TYPE = 'application/json; charset=UTF-8'
API_CONTENT_ENCODING = 'amz-1.0'

RELAY_STATE = f'https://{DEFAULT_AWS_REGION}.console.aws.amazon.com/console/home?region={DEFAULT_AWS_REGION}#'
