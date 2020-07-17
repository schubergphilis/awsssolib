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
import copy
import json
from awsssolib.awsssolibexceptions import UnsupportedTarget
from awsssolib.configuration import (SUPPORTED_TARGETS,
                                     DEFAULT_AWS_REGION,
                                     API_CONTENT_TYPE,
                                     API_CONTENT_ENCODING)


def get_api_payload(content_string,  # pylint: disable=too-many-arguments
                    target, method='POST',
                    params=None,
                    path='/',
                    content_type=API_CONTENT_TYPE,
                    content_encoding=API_CONTENT_ENCODING,
                    x_amz_target='',
                    region=DEFAULT_AWS_REGION):
    """Generates the payload for calling the AWS SSO APIs.

    Returns:
        deepcopy: Returns a deepcopy object of the payload

    """
    target = _validate_target(target)
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


def _validate_target(target):
    if target not in SUPPORTED_TARGETS:
        raise UnsupportedTarget(target)
    return target
