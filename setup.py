# -*- coding: utf-8 -*-

# Copyright (C) 2019  Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import io
import os
import setuptools  # type: ignore

version = "1.2.0"

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.rst")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

dependencies = [
    "google-cloud-pubsub >= 2.1.0, <3.0.0dev",
    "grpcio >= 1.18.0",
    "grpcio-status >= 1.18.0",
    "overrides>=6.0.1, <7.0.0",
    "packaging >= 14.3",
]

setuptools.setup(
    name="google-cloud-pubsublite",
    version=version,
    long_description=readme,
    author="Google LLC",
    author_email="googleapis-packages@google.com",
    license="Apache 2.0",
    url="https://github.com/googleapis/python-pubsublite",
    packages=[
        package
        for package in setuptools.PEP420PackageFinder.find()
        if package.startswith("google")
    ],
    namespace_packages=("google", "google.cloud"),
    platforms="Posix; MacOS X; Windows",
    include_package_data=True,
    install_requires=dependencies,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)
