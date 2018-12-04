#  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License").
#  You may not use this file except in compliance with the License.
#  A copy of the License is located at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  or in the "license" file accompanying this file. This file is distributed
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#  express or implied. See the License for the specific language governing
#  permissions and limitations under the License.
from __future__ import absolute_import

import os

import pytest
import requests
from sagemaker.mxnet.model import MXNetModel

import local_mode_utils
from test.integration import NUM_MODEL_SERVER_WORKERS, RESOURCE_PATH


@pytest.fixture(scope='module')
def predictor(docker_image, sagemaker_local_session, local_instance_type):
    default_handler_path = os.path.join(RESOURCE_PATH, 'default_handlers')
    m = MXNetModel('file://{}'.format(os.path.join(default_handler_path, 'model')), 'SageMakerRole',
                   os.path.join(default_handler_path, 'code', 'empty_module.py'),
                   image=docker_image, sagemaker_session=sagemaker_local_session,
                   model_server_workers=NUM_MODEL_SERVER_WORKERS)
    with local_mode_utils.lock():
        try:
            predictor = m.deploy(1, local_instance_type)
            yield predictor
        finally:
            sagemaker_local_session.delete_endpoint(m.endpoint_name)


def test_default_model_fn(predictor):
    input = [[1, 2]]
    output = predictor.predict(input)
    assert [[4.9999918937683105]] == output


def test_default_model_fn_content_type(predictor):
    r = requests.post('http://localhost:8080/invocations', json=[[1, 2]])
    assert 'application/json' == r.headers['Content-Type']
    assert [[4.9999918937683105]] == r.json()
