#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: core.py
#
# Copyright 2018 Sayantan Khanra
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
Main code for core.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging


__author__ = '''Sayantan Khanra <sKhanra@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''2018-01-08'''
__copyright__ = '''Copyright 2018, Sayantan Khanra'''
__credits__ = ["Sayantan Khanra"]
__license__ = '''MIT'''
__maintainer__ = '''Sayantan Khanra'''
__email__ = '''<sKhanra@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''core'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class LoggerMixin:  # pylint: disable=too-few-public-methods
    """Logger."""

    @property
    def logger(self):
        """Exposes the logger to be used by objects using the Mixin.

        Returns:
            logger (logger): The properly named logger.

        """
        return logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')


class Entity(LoggerMixin):  # pylint: disable=too-few-public-methods
    """The core object of okta."""

    def __init__(self, sso_instance, data):
        logger_name = u'{base}.{suffix}'.format(base=LOGGER_BASENAME,
                                                suffix=self.__class__.__name__)
        self._logger = logging.getLogger(logger_name)
        self._sso = sso_instance
        self._data = self._parse_data(data)

    def _parse_data(self, data):
        if not isinstance(data, dict):
            self._logger.error('Invalid data received :{}'.format(data))
            data = {}
        return data
