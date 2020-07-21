#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: entities.py
#
# Copyright 2020 Sayantan Khanra, Costas Tyfoxylos
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
Main code for entities.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
import json

from awsauthenticationlib import LoggerMixin

__author__ = '''Sayantan Khanra <skhanra@schubergphilis.com>, <ctyfoxylos@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''18-05-2020'''
__copyright__ = '''Copyright 2020, Sayantan Khanra, Costas Tyfoxylos'''
__credits__ = ["Sayantan Khanra", "Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Sayantan Khanra, Costas Tyfoxylos'''
__email__ = '''<skhanra@schubergphilis.com>, <ctyfoxylos@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''entities'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class Entity(LoggerMixin):  # pylint: disable=too-few-public-methods
    """The core entity."""

    def __init__(self, sso_instance, data):
        self._sso = sso_instance
        self._data = self._parse_data(data)

    def _parse_data(self, data):
        if not isinstance(data, dict):
            self.logger.error('Invalid data received :{}'.format(data))
            data = {}
        return data


class Group(Entity):
    """Models the group object of AWS SSO."""

    def __init__(self, sso_instance, data):
        super().__init__(sso_instance, data)
        self.url = f'{sso_instance.api_url}/userpool'

    @property
    def id(self):  # pylint: disable=invalid-name
        """The id of the group.

        Returns:
            id (str) : The id of the group

        """
        return self._data.get('GroupId')

    @property
    def name(self):
        """The name of the group.

        Returns:
            string: The name of the group

        """
        return self._data.get('GroupName', '')

    @property
    def description(self):
        """The description of the group.

        Returns:
            str: The description of the group

        """
        return self._data.get('Description', '')

    @property
    def users(self):
        """The users in the group.

        Returns:
            str: The users part of the group

        """
        payload = self._sso.get_api_payload(content_string={'GroupId': self.id,
                                                            'MaxResults': 100},
                                            target='ListMembersInGroup',
                                            path='/userpool/',
                                            x_amz_target='com.amazonaws.swbup.service.SWBUPService.ListMembersInGroup'
                                            )
        self.logger.debug('Trying to get users for the groups...')
        response = self._sso.session.post(self.url,
                                          json=payload)
        if not response.ok:
            self.logger.error(response.text)
            return []
        return response.json().get('Members', [])


class Account(Entity):
    """Models the Account object of AWS SSO."""

    def __init__(self, sso_instance, data):
        super().__init__(sso_instance, data)
        self.url = sso_instance.endpoint_url
        self._instance_id = None

    @property
    def name(self):
        """The name of the application.

        Returns:
            basestring: The name of the application

        """
        return self._data.get('Name')

    @property
    def email(self):
        """The name of the application.

        Returns:
            basestring: The name of the application

        """
        return self._data.get('Email')

    @property
    def id(self):  # pylint: disable=invalid-name
        """The name of the application.

        Returns:
            basestring: The name of the application

        """
        return self._data.get('Id')

    @property
    def arn(self):
        """The name of the application.

        Returns:
            basestring: The name of the application

        """
        return self._data.get('Arn')

    @property
    def status(self):
        """The name of the application.

        Returns:
            basestring: The name of the application

        """
        return self._data.get('Status')

    @property
    def instance_id(self):
        """The instance_id of the Account.

        Returns:
            str: The instance_id of the account

        """
        if self._instance_id is None:
            account_id = self.id
            target = 'com.amazon.switchboard.service.SWBService.GetApplicationInstanceForAWSAccount'
            payload = self._sso.get_api_payload(content_string={'awsAccountId': account_id},
                                                target='GetApplicationInstanceForAWSAccount',
                                                path='/control/',
                                                x_amz_target=target)
            self.logger.debug('Trying to get instance id for aws account...')
            response = self._sso.session.post(self.url,
                                              json=payload)
            self._instance_id = response.json().get('applicationInstance', {}).get('instanceId', '')
        return self._instance_id

    @property
    def associated_profiles(self):
        """The associated profiles with the Account.

        Returns:
            list: The list of associated profiles with the Account

        """
        target = 'com.amazon.switchboard.service.SWBService.ListAWSAccountProfiles'
        payload = self._sso.get_api_payload(content_string={'instanceId': self.instance_id},
                                            target='ListAWSAccountProfiles',
                                            path='/control/',
                                            x_amz_target=target)
        self.logger.debug('Trying to provision application profile for aws account...')
        response = self._sso.session.post(self.url,
                                          json=payload)
        if not response.ok:
            self.logger.error(response.text)
            return []
        return response.json().get('profileList', [])


class User(Entity):
    """Models the user object of SSO."""

    def __init__(self, sso_instance, data):
        super().__init__(sso_instance, data)
        self.url = f'{sso_instance.api_url}/userpool'

    @property
    def status(self):
        """The status of the user.

        Returns:
            string: The status of the user

        """
        return self._data.get('Active')

    @property
    def created_at(self):
        """The date and time of the users's activation.

        Returns:
            datetime: The datetime object of when the user was activated

        """
        return self._data.get('Meta', {}).get('CreatedAt')

    @property
    def updated_at(self):
        """The date and time of the users's status change.

        Returns:
            datetime: The datetime object of when the user had last changed status

        """
        return self._data.get('Meta', {}).get('UpdatedAt')

    @property
    def emails(self):
        """The date and time of the users's last password change.

        Returns:
            datetime: The datetime object of when the user last changed password

        """
        return self._data.get('UserAttributes').get('emails', {}).get('ComplexListValue', '')

    @property
    def _name(self):
        return self._data.get('UserAttributes').get('name', {}).get('ComplexValue', {})

    @property
    def first_name(self):
        """The first name of the user.

        Returns:
            string: The first name of the user

        """
        return self._name.get('givenName', {}).get('StringValue', '')

    @property
    def last_name(self):
        """The last name of the user.

        Returns:
            string: The last name of the user

        """
        return self._name.get('familyName', {}).get('StringValue', '')

    @property
    def id(self):  # pylint: disable=invalid-name
        """The manager of the user.

        Returns:
            string: The manager of the user

        """
        return self._data.get('UserId')

    @property
    def name(self):
        """The manager of the user.

        Returns:
            str: The manager of the user

        """
        return self._data.get('UserName')

    @property
    def display_name(self):
        """The display name of the user.

        Returns:
            str: The display name of the user

        """
        return self._data.get('UserAttributes', {}).get('displayName', {}).get('StringValue')

    @property
    def groups(self):
        """The groups associated with the user.

        Returns:
            str: The groups associated with the user

        """
        payload = self._sso.get_api_payload(content_string={'UserId': self.id,
                                                            'MaxResults': 100},
                                            target='ListGroupsForUser',
                                            path='/userpool/',
                                            x_amz_target='com.amazonaws.swbup.service.SWBUPService.ListGroupsForUser')
        self.logger.debug('Trying to get groups for the user...')
        response = self._sso.session.post(self.url,
                                          json=payload)
        if not response.ok:
            self.logger.error(response.text)
            return []
        return response.json().get('Groups', [])


class PermissionSet(Entity):
    """Models the permissionset object of SSO."""

    def __init__(self, sso_instance, data):
        super().__init__(sso_instance, data)
        self.url = sso_instance.endpoint_url

    @property
    def description(self):
        """The status of the user.

        Returns:
            string: The status of the user

        """
        return self._data.get('Description')

    @property
    def id(self):  # pylint: disable=invalid-name
        """The status of the user.

        Returns:
            string: The status of the user

        """
        return self._data.get('Id')

    @property
    def name(self):
        """The status of the user.

        Returns:
            string: The status of the user

        """
        return self._data.get('Name')

    @property
    def ttl(self):
        """The status of the user.

        Returns:
            string: The status of the user

        """
        return self._data.get('ttl')

    @property
    def creation_date(self):
        """The status of the user.

        Returns:
            string: The status of the user

        """
        return self._data.get('CreationDate')

    @property
    def relay_state(self):
        """The relay_state of the permission_set.

        Returns:
            string: The relayState of the permission_set

        """
        return self._data.get('relayState')

    @property
    def permission_policy(self):
        """The relayState of the permission_set.

        Returns:
            string: The relayState of the permission_set

        """
        target = 'com.amazon.switchboard.service.SWBService.GetPermissionsPolicy'
        content_string = {'permissionSetId': self.id}
        payload = self._sso.get_api_payload(content_string=content_string,
                                            target='GetPermissionsPolicy',
                                            path='/control/',
                                            x_amz_target=target)
        response = self._sso.session.post(self.url,
                                          json=payload)
        if not response.ok:
            self.logger.error(response.text)
            return None
        return response.json()

    @property
    def provisioned_accounts(self):
        """The provisioned accounts with the permission set.

        Returns:
            list: Accounts provisioned with the permission set

        """
        account_list = []
        account_ids, marker = self._list_provisioned_accounts_pagination()
        while marker:
            accountids, marker = self._list_provisioned_accounts_pagination(marker=marker)
            account_ids = account_ids + accountids
        for account_id in account_ids:
            account_list.append(self._sso.get_account_by_id(account_id))
        return account_list

    def _list_provisioned_accounts_pagination(self, marker=None):
        target = 'com.amazon.switchboard.service.SWBService.ListAccountsWithProvisionedPermissionSet'
        if not marker:
            content_string = {'permissionSetId': self.id,
                              'onlyOutOfSync': 'false'}
        else:
            content_string = {'permissionSetId': self.id,
                              'onlyOutOfSync': 'false',
                              'marker': marker}
        payload = self._sso.get_api_payload(content_string=content_string,
                                            target='ListAccountsWithProvisionedPermissionSet',
                                            path='/control/',
                                            x_amz_target=target
                                            )
        self.logger.debug('Trying to list accounts details...')
        response = self._sso.session.post(self.url,
                                          json=payload)
        if not response.ok:
            self.logger.error(response.text)
            return [], None
        return response.json().get('accountIds', []), response.json().get('marker', '')

    def assign_custom_policy_to_permission_set(self,
                                               policy_document
                                               ):
        """Assign Custom policy to a permission_set.

        Args:
            permission_set_name: The name of the permission_set .
            policy_document: The policy for the permission_set
        Returns:
            Bool:  True or False

        """
        content_string = {'permissionSetId': self.id,
                          'policyDocument': json.dumps(policy_document)
                          }
        target = 'com.amazon.switchboard.service.SWBService.PutPermissionsPolicy'
        payload = self._sso.get_api_payload(content_string=content_string,
                                            target='PutPermissionsPolicy',
                                            path='/control/',
                                            x_amz_target=target)
        response = self._sso.session.post(self.url,
                                          json=payload)
        if not response.ok:
            self.logger.error(response.text)
        return response.ok

    def update(self, description=' ', relay_state='', ttl=''):
        """The relayState of the permission_set.

        Args:
            description: Description for the permission set
            relay_state: The relay state for the permission set.
                                 https://docs.aws.amazon.com/singlesignon/latest/userguide/howtopermrelaystate.html
            ttl: session duration

        Returns:
            bool: True or False

        """
        content_string = {'permissionSetId': self.id,
                          'description': description if description != ' ' else self.description,
                          'ttl': ttl if ttl else self.ttl,
                          'relayState': relay_state if relay_state else self.relay_state}
        target = 'com.amazon.switchboard.service.SWBService.UpdatePermissionSet'
        payload = self._sso.get_api_payload(content_string=content_string,
                                            target='UpdatePermissionSet',
                                            path='/control/',
                                            x_amz_target=target)
        response = self._sso.session.post(self.url,
                                          json=payload)
        if not response.ok:
            self.logger.error(response.text)
        return response.ok
