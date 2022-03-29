# Copyright 2020 Google LLC
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

"""This script is used to synthesize generated parts of this library."""
import os

import synthtool as s
import synthtool.gcp as gcp
from synthtool.languages import python

common = gcp.CommonTemplates()

default_version = "v1"

for library in s.get_staging_dirs(default_version):
    excludes = [
        "docs/pubsublite_v1",  # generated GAPIC docs should be ignored
        "docs/index.rst",
        "google/cloud/pubsublite/__init__.py",
        "README.rst",
        "scripts/fixup*.py",  # new libraries do not need the keyword fixup script
        "setup.py",
        "noxfile.py",  # exclude to opt-in to pytype
    ]
    s.move(library, excludes=excludes)

s.remove_staging_dirs()

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(
    cov_level=96,
    microgenerator=True,
    system_test_external_dependencies=["asynctest"],
    unit_test_external_dependencies=["asynctest"],
)

s.move(
    templated_files, 
    excludes=[
        ".coveragerc", # the microgenerator has a good coveragerc file
        "docs/multiprocessing.rst",  # exclude multiprocessing note
    ]
)  


s.replace(
    "noxfile.py",
    """\
BLACK_VERSION = "black==22.3.0"
""",
    """\
PYTYPE_VERSION = "pytype==2021.09.09"
BLACK_VERSION = "black==22.3.0"
""",
)

# add pytype to nox.options.sessions
s.replace("noxfile.py",
    """nox.options.sessions = \[
    "unit",""",
    """nox.options.sessions = [
    "unit",
    "pytype", # Custom pytype session""",
)

# Extract installing dependencies into separate function
s.replace("noxfile.py",
"""def default\(session\):
    # Install all test dependencies, then install this package in-place.
""",

"""def install_test_deps(session):"""
)

# Restore function `default()``
s.replace("noxfile.py",
"""# Run py.test against the unit tests.""",
"""
def default(session):
    # Install all test dependencies, then install this package in-place.
    install_test_deps(session)

    # Run py.test against the unit tests."""
)

# add pytype nox session
s.replace("noxfile.py",
"""
@nox.session\(python=DEFAULT_PYTHON_VERSION\)
def docfx\(session\):""",
"""
@nox.session(python=DEFAULT_PYTHON_VERSION)
def pytype(session):
    \"\"\"Run type checks.\"\"\"
    install_test_deps(session)
    session.install(PYTYPE_VERSION)
    session.run("pytype", "google/cloud/pubsublite")

@nox.session(python=DEFAULT_PYTHON_VERSION)
def docfx(session):"""
)

# Work around bug in templates https://github.com/googleapis/synthtool/pull/1335
s.replace(".github/workflows/unittest.yml", "--fail-under=100", "--fail-under=96")

python.py_samples(skip_readmes=True)

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
