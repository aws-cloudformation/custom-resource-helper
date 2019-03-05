
"""
Copyright 2016-2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the
License. A copy of the License is located at
    http://aws.amazon.com/apache2.0/
or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import setup, find_packages

setup(
    name="crhelper",
    version="1.0.0",
    description="crhelper simplifies authoring CloudFormation Custom Resources",
    url="https://github.com/awslabs/aws-cloudformation-templates/tree/master/community/custom_resources/python_custom_resource_helper",
    author="Jay McConnell",
    author_email="jmmccon@amazon.com",
    license="Apache2",
    packages=find_packages(),
    test_suite="tests.unit"
)
