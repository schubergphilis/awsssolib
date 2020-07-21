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

import logging
import json
from awsauthenticatorlib import AwsAuthenticator, LoggerMixin, Urls
from awsssolib.configuration import SUPPORTED_TARGETS, RELAY_STATE
from .entities import (Group,
                       User,
                       Account,
                       PermissionSet)

__author__ = '''Sayantan Khanra <skhanra@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''18-05-2020'''
__copyright__ = '''Copyright 2020, Sayantan Khanra'''
__credits__ = ["Sayantan Khanra", "Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Sayantan Khanra'''
__email__ = '''<skhanra@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''awsssolib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class Sso(LoggerMixin):
    """Models AWS SSO."""
    API_CONTENT_TYPE = 'application/json; charset=UTF-8'
    API_CONTENT_ENCODING = 'amz-1.0'
    DEFAULT_AWS_REGION = 'eu-west-1'

    def __init__(self, arn):
        self.aws_authenticator = AwsAuthenticator(arn)
        self._urls = Urls(self.aws_region)
        self.session = self._get_authenticated_session()

    @property
    def relay_state(self):
        return f'{self._urls.regional_console}home?region={self.aws_region}#'

    @property
    def api_url(self):
        return f'{self._urls.regional_single_sign_on}/api'

    @property
    def endpoint_url(self):
        return f'{self.api_url}/peregrine'

    @property
    def aws_region(self):
        """Aws Console Region.

        Returns:
            region (str): The region of the console.

        """
        return self.aws_authenticator.region

    @staticmethod
    def get_api_payload(content_string,  # pylint: disable=too-many-arguments
                        target,
                        method='POST',
                        params=None,
                        path='/',
                        content_type=Sso.API_CONTENT_TYPE,
                        content_encoding=Sso.API_CONTENT_ENCODING,
                        x_amz_target='',
                        region=Sso.DEFAULT_AWS_REGION):
        """Generates the payload for calling the AWS SSO APIs.

        Returns:
            deepcopy: Returns a deepcopy object of the payload

        """
        target = Sso._validate_target(target)
        payload = {'contentString': json.dumps(content_string),
                   'headers': {'Content-Type': content_type,
                               'Content-Encoding': content_encoding,
                               'X-Amz-Target': x_amz_target},
                   'method': method,
                   'operation': target,
                   'params': params or {},
                   'path': path,
                   'region': region}
        return copy.deepcopy(payload)

    @staticmethod
    def _validate_target(target):
        if target not in SUPPORTED_TARGETS:
            raise UnsupportedTarget(target)
        return target

    def _get_authenticated_session(self):
        return self.aws_authenticator.get_sso_authenticated_session()

    @property
    def sso_directory_id(self):
        """The external/internal directory id configured with aws sso.

        Returns:
           str: The id of directory configured in SSO

        """
        payload = Sso.get_api_payload(content_string={},
                                      target='GetUserPoolInfo',
                                      path='/userpool/',
                                      x_amz_target='com.amazonaws.swbup.service.SWBUPService.GetUserPoolInfo',
                                      region=self.aws_region)
        self.logger.debug('Trying to get directory id for sso')
        response = self.session.post(f'{self.api_url}/userpool', json=payload)
        if not responce.ok:
            self.logger.error(f'Error! Received :{response.text}')
            return None
        return response.json().get('DirectoryId')

    @property
    def accounts(self):
        """The aws accounts in aws sso.

        Returns:
            list: The id of directory configured in SSO

        """
        accounts, next_token = self._list_accounts_pagination()
        while next_token:
            account_list, next_token = self._list_accounts_pagination(next_token=next_token)
            accounts = accounts + account_list
        return accounts

    @property
    def users(self):
        """The users configured in SSO.

        Returns:
            list: The list of groups configured in SSO

        """
        content_payload = {"IdentityStoreId": self.sso_directory_id,
                           "MaxResults": 25}
        path = 'identitystore'
        target = 'SearchUsers'
        amz_target = 'com.amazonaws.identitystore.AWSIdentityStoreService.SearchUsers'
        region = self.aws_region
        return self._get_paginated_results(content_payload,
                                           path,
                                           target,
                                           amz_target,
                                           region,
                                           object_type=User,
                                           object_group='Users')

    @property
    def groups(self):
        """The groups configured in SSO.

        Returns:
            list: The list of groups configured in SSO

        """
        content_payload = {"SearchString": "*",
                           "SearchAttributes": ["GroupName"],
                           "MaxResults": 100}
        path = 'userpool'
        target = 'SearchGroups'
        amz_target = 'com.amazonaws.swbup.service.SWBUPService.SearchGroups'
        region = self.aws_region
        return self._get_paginated_results(content_payload,
                                           path,
                                           target,
                                           amz_target,
                                           region,
                                           object_type=Group,
                                           object_group='Groups')

    @property
    def permission_sets(self):
        """The permission_sets configured in SSO.

        Returns:
            list: The list of groups configured in SSO

        """
        payload = Sso.get_api_payload(content_string={},
                                      target='ListPermissionSets',
                                      path='/control/',
                                      x_amz_target='com.amazon.switchboard.service.SWBService.ListPermissionSets',
                                      region=self.aws_region
                                      )
        self.logger.debug('Trying to account details...')
        response = self.session.post(self.endpoint_url,
                                     json=payload)
        return [PermissionSet(self, data) for data in response.json().get('permissionSets')]

    def get_user_by_name(self, user_name):
        """The user configured in SSO.

        Returns:
            User: The User object

        """
        return next((user for user in self.users if user.name == user_name), None)

    def get_user_by_id(self, user_id):
        """The user configured in SSO.

        Returns:
            User: The User object

        """
        return next((user for user in self.users if user.id == user_id), None)

    def get_group_by_name(self, group_name):
        """The group configured in SSO.

        Returns:
            Group: The Group object

        """
        return next((group for group in self.groups if group.name == group_name), None)

    def get_group_by_id(self, group_id):
        """The group configured in SSO.

        Returns:
            Group: The Group object

        """
        return next((group for group in self.groups if group.id == group_id), None)

    def get_account_by_name(self, account_name):
        """The account configured in SSO.

        Returns:
            Account: The Account object

        """
        return next((account for account in self.accounts if account.name == account_name), None)

    def get_account_by_id(self, account_id):
        """The account configured in SSO.

        Returns:
            Account: The Account object

        """
        return next((account for account in self.accounts if account.id == account_id), None)

    def get_permission_set_by_name(self, permission_set_name):
        """The permission-set configured in SSO.

        Returns:
            PermissionSet: The PermissionSet object

        """
        return next(
            (permission_set for permission_set in self.permission_sets if permission_set.name == permission_set_name),
            None)

    def _provision_application_profile_for_aws_account_instance(self, permission_set_name, account_name):
        method = 'ProvisionApplicationProfileForAWSAccountInstance'
        permission_set_id = self.get_permission_set_by_name(permission_set_name).id
        instance_id = self.get_account_by_name(account_name).instance_id
        payload = Sso.get_api_payload(content_string={'permissionSetId': permission_set_id,
                                                      'instanceId': instance_id},
                                      target=method,
                                      path='/control/',
                                      x_amz_target=f'com.amazon.switchboard.service.SWBService.{method}',
                                      region=self.aws_region
                                      )
        self.logger.debug('Trying to provision application profile for aws account...')
        response = self.session.post(self.endpoint_url,
                                     json=payload)
        return response.json().get('applicationProfile', {}).get('profileId', '')

    def _get_aws_account_profile_for_permission_set(self, account_name, permission_set_name):
        return next((profile for profile in self.get_account_by_name(account_name).associated_profiles if
                     profile.get('name') == permission_set_name), {})

    def associate_group_to_account(self, group_name, account_name, permission_set_name):
        """Associates a group with an account with proper permissions.

        Args:
            group_name: The name of the group to be assigned.
            account_name: Name of the account to which the group will be assigned
            permission_set_name: the Permission Set the group will have on the account

        Returns:
            bool: True or False

        """
        group_id = self.get_group_by_name(group_name).id
        instance_id = self.get_account_by_name(account_name).instance_id
        profile_id = self._provision_application_profile_for_aws_account_instance(permission_set_name, account_name)
        directory_id = self.sso_directory_id
        content_string = {'accessorId': group_id,
                          'accessorType': 'GROUP',
                          'accessorDisplay': {"groupName": group_name},
                          'instanceId': instance_id,
                          'profileId': profile_id,
                          'directoryType': 'UserPool',
                          'directoryId': directory_id}
        payload = Sso.get_api_payload(content_string=content_string,
                                      target='AssociateProfile',
                                      path='/control/',
                                      x_amz_target='com.amazon.switchboard.service.SWBService.AssociateProfile',
                                      region=self.aws_region
                                      )
        self.logger.debug('Trying to assign groups to aws account...')
        response = self.session.post(self.endpoint_url,
                                     json=payload)
        return response.ok

    def disassociate_group_from_account(self, group_name, account_name, permission_set_name):
        """Disassociates a group with an account with proper permissions.

        Args:
            group_name: The name of the group to be assigned.
            account_name: Name of the account to which the group will be assigned
            permission_set_name: the Permission Set the group will have on the account

        Returns:
            bool: True or False

        """
        group_id = self.get_group_by_name(group_name).id
        instance_id = self.get_account_by_name(account_name).instance_id
        directory_id = self.sso_directory_id
        profile_id = self._get_aws_account_profile_for_permission_set(account_name, permission_set_name).get(
            'profileId')
        content_string = {'accessorId': group_id,
                          'accessorType': 'GROUP',
                          'accessorDisplay': {"groupName": group_name},
                          'instanceId': instance_id,
                          'profileId': profile_id,
                          'directoryType': 'UserPool',
                          'directoryId': directory_id}
        payload = Sso.get_api_payload(content_string=content_string,
                                      target='DisassociateProfile',
                                      path='/control/',
                                      x_amz_target='com.amazon.switchboard.service.SWBService.DisassociateProfile',
                                      region=self.aws_region
                                      )
        self.logger.debug('Trying to assign groups to aws account...')

        response = self.session.post(self.endpoint_url,
                                     json=payload)
        LOGGER.debug(response)
        return response.ok

    def associate_user_to_account(self, user_name, account_name, permission_set_name):
        """Associates an user with an account with proper permissions.

        Args:
            user_name: The name of the user to be assigned.
            account_name: Name of the account to which the user will be assigned
            permission_set_name: the Permission Set the user will have on the account

        Returns:
            bool: True or False

        """
        user = self.get_user_by_name(user_name)
        user_id = user.id
        user_first_name = user.first_name
        user_last_name = user.last_name
        instance_id = self.get_account_by_name(account_name).instance_id
        profile_id = self._provision_application_profile_for_aws_account_instance(permission_set_name, account_name)
        directory_id = self.sso_directory_id
        content_string = {'accessorId': user_id,
                          'accessorType': 'USER',
                          'accessorDisplay': {"userName": user_name,
                                              "firstName": user_first_name,
                                              "last_name": user_last_name,
                                              "windowsUpn": user_name},
                          'instanceId': instance_id,
                          'profileId': profile_id,
                          'directoryType': 'UserPool',
                          'directoryId': directory_id}
        payload = Sso.get_api_payload(content_string=content_string,
                                      target='AssociateProfile',
                                      path='/control/',
                                      x_amz_target='com.amazon.switchboard.service.SWBService.AssociateProfile',
                                      region=self.aws_region
                                      )
        self.logger.debug('Trying to assign groups to aws account...')
        response = self.session.post(self.endpoint_url,
                                     json=payload)
        return response.ok

    def disassociate_user_from_account(self, user_name, account_name, permission_set_name):
        """Disassociates an user with an account with proper permissions.

        Args:
            user_name: The name of the user to be assigned.
            account_name: Name of the account to which the user will be assigned
            permission_set_name: the Permission Set the user will have on the account

        Returns:
            bool: True or False

        """
        user = self.get_user_by_name(user_name)
        user_id = user.id
        user_first_name = user.first_name
        user_last_name = user.last_name
        instance_id = self.get_account_by_name(account_name).instance_id
        directory_id = self.sso_directory_id
        profile_id = self._get_aws_account_profile_for_permission_set(account_name, permission_set_name).get(
            'profileId')
        content_string = {'accessorId': user_id,
                          'accessorType': 'USER',
                          'accessorDisplay': {"userName": user_name,
                                              "firstName": user_first_name,
                                              "last_name": user_last_name,
                                              "windowsUpn": user_name},
                          'instanceId': instance_id,
                          'profileId': profile_id,
                          'directoryType': 'UserPool',
                          'directoryId': directory_id}
        payload = Sso.get_api_payload(content_string=content_string,
                                      target='DisassociateProfile',
                                      path='/control/',
                                      x_amz_target='com.amazon.switchboard.service.SWBService.DisassociateProfile',
                                      region=self.aws_region
                                      )
        self.logger.debug('Trying to assign groups to aws account...')

        response = self.session.post(self.endpoint_url,
                                     json=payload)
        self.logger.debug(response)
        return response.ok

    def _list_accounts_pagination(self, next_token=None):
        content_string = {} if not next_token else {'NextToken': next_token}
        payload = {'contentString': json.dumps(content_string),
                   'headers': {'Content-Type': 'application/x-amz-json-1.1',
                               'Content-Encoding': "amz-1.0",
                               'X-Amz-Target': 'AWSOrganizationsV20161128.ListAccounts',
                               'X-Amz-User-Agent': 'aws-sdk-js/2.152.0 promise'},
                   'method': 'POST',
                   'operation': 'listAccounts',
                   'params': {},
                   'path': '/',
                   'region': 'us-east-1'}
        self.logger.debug('Trying to list account details...')
        response = self.session.post(f'{self.api_url}/organizations',
                                     json=payload)
        return [Account(self, data) for data in response.json().get('Accounts')], response.json().get('NextToken', '')

    # def _list_users_pagination(self, next_token=None):
    #     content_string = {"IdentityStoreId": self.sso_directory_id,
    #                       "MaxResults": 25}
    #     if next_token:
    #         content_string.update({'NextToken': next_token})
    #     path = 'identitystore'
    #     payload = Sso.get_api_payload(content_string=content_string,
    #                                   target='SearchUsers',
    #                                   path=f'/{path}/',
    #                                   x_amz_target='com.amazonaws.identitystore.AWSIdentityStoreService.SearchUsers',
    #                                   region=self.aws_region
    #                                   )
    #     self.logger.debug('Trying to list user details...')
    #     response = self.session.post(f'{self.api_url}/{path}',
    #                                  json=payload)
    #     return [User(self, data) for data in response.json().get('Users')], response.json().get('NextToken', '')

    # def _list_groups_pagination(self, next_token=None):
    #     self.logger.debug('Trying to get group list in sso')
    #
    #     if next_token:
    #         content_string.update({'NextToken': next_token})
    #
    #     payload = Sso.get_api_payload(content_string=content_string,
    #                                   target='SearchGroups',
    #                                   path=f'/{path}/',
    #                                   x_amz_target='com.amazonaws.swbup.service.SWBUPService.SearchGroups',
    #                                   region=self.aws_region
    #                                   )
    #     response = self.session.post(f'{self.api_url}/{path}',
    #                                  json=payload)
    #     return [Group(self, data) for data in response.json().get('Groups')], response.json().get('NextToken', '')

    def _get_paginated_results(self,
                               content_payload,
                               path,
                               target,
                               amz_target,
                               region,
                               object_type,
                               object_group):
        payload = Sso.get_api_payload(content_string=content_payload,
                                      target=target,
                                      path=f'/{path}/',
                                      x_amz_target=amz_target,
                                      region=region)
        url = f'{self.api_url}/{path}'
        response, next_token = self._get_partial_response(url, payload)
        for data in response.json().get(object_group, []):
            yield object_type(self, data)
        while next_token:
            payload.update({'NextToken': next_token})
            response, next_token = self._get_partial_response(url, payload)
            for data in response.json().get(object_group, []):
                yield object_type(self, data)

    def _get_partial_response(self, url, payload):
        response = self.session.post(url, json=payload)
        if not response.ok:
            raise SystemError(response.text)
        next_token = response.json().get('NextToken')
        return response, next_token

    def create_permission_set(self,
                              name,
                              description=' ',
                              relay_state=self.relay_state,
                              ttl='PT2H'):
        """Create a permission_set with a aws defined policy or custom policy.

        Args:
                    name: The name of the permission_set .
                    description: Description for the permission set
                    relay_state: The relay state for the permission set.
                                 https://docs.aws.amazon.com/singlesignon/latest/userguide/howtopermrelaystate.html
                    ttl: session duration
        Returns:
                    PermissionSet: Permission Set object

        """
        content_string = {'permissionSetName': name,
                          'description': description,
                          'relayState': relay_state,
                          'ttl': ttl
                          }
        payload = Sso.get_api_payload(content_string=content_string,
                                      target='CreatePermissionSet',
                                      path='/control/',
                                      x_amz_target='com.amazon.switchboard.service.SWBService.CreatePermissionSet',
                                      region=self.aws_region
                                      )
        self.logger.debug('Trying to create Permission set...')

        response = self.session.post(self.endpoint_url,
                                     json=payload)
        self.logger.debug(response)
        return PermissionSet(self, response.json().get('permissionSet'))
