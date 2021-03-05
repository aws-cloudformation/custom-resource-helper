
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


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="crhelper",
    version="2.0.8",
    description="crhelper simplifies authoring CloudFormation Custom Resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aws-cloudformation/custom-resource-helper",
    author="Jay McConnell",
    author_email="jmmccon@amazon.com",
    license="Apache2",
    packages=find_packages(),
    install_requires=[],
    tests_require=["boto3"],
    test_suite="tests",
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
