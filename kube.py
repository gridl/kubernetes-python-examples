#!/usr/bin/env python

# This entire file exists to monkeypatch this issue:
# https://github.com/kubernetes-client/python-base/issues/65
from six import PY3
import asyncio
import logging
import json
import argparse
import base64
import datetime

from kubernetes import client, config, watch

from kubernetes.config.kube_config import _is_expired

from kubernetes.config.dateutil import UTC, format_rfc3339, parse_rfc3339

def local_load_oid_token(self, provider):
    if 'config' not in provider:
        return

    parts = provider['config']['id-token'].split('.')

    if len(parts) != 3:  # Not a valid JWT
        return None

    padding = (4 - len(parts[1]) % 4) * '='

    if PY3:
        jwt_attributes = json.loads(
            base64.urlsafe_b64decode(parts[1] + padding).decode('utf-8')
        )
    else:
        jwt_attributes = json.loads(
            base64.b64decode(parts[1] + padding)
        )

    expire = jwt_attributes.get('exp')

    if ((expire is not None) and
        (_is_expired(datetime.datetime.fromtimestamp(expire,
                                                    tz=UTC)))):
        self._refresh_oidc(provider)

        if self._config_persister:
            self._config_persister(self._config.value)

    self.token = "Bearer %s" % provider['config']['id-token']

    return self.token

config.kube_config.KubeConfigLoader._load_oid_token = local_load_oid_token
