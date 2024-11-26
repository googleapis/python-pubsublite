# Copyright 2022 Google LLC
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

import json
from pathlib import Path
import shutil

import synthtool as s
import synthtool.gcp as gcp
from synthtool.languages import python

# ----------------------------------------------------------------------------
# Copy the generated client from the owl-bot staging directory
# ----------------------------------------------------------------------------

clean_up_generated_samples = True

# Load the default version defined in .repo-metadata.json.
default_version = json.load(open(".repo-metadata.json", "rt")).get("default_version")

for library in s.get_staging_dirs(default_version):
    if clean_up_generated_samples:
        shutil.rmtree("samples/generated_samples", ignore_errors=True)
        clean_up_generated_samples = False

    # temporarily workaround issue with generated code
    s.replace(
        library / "google/cloud/pubsublite_v1/__init__.py",
        "from google.cloud.pubsublite import gapic_version as package_version",
        "from google.cloud.pubsublite_v1 import gapic_version as package_version",
    )

    s.move(
        [library],
        excludes=[
            "**/gapic_version.py",  # gapic_version.py will be updated by release please
            "docs/**/*",  # generated GAPIC docs should be ignored
            "scripts/fixup*.py",  # new libraries do not need the keyword fixup script
            "setup.py",
            "testing/constraints-3.7.txt",
            "testing/constraints-3.8.txt",
            "google/cloud/pubsublite/__init__.py",
            "README.rst",
        ],
    )
s.remove_staging_dirs()

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------

templated_files = gcp.CommonTemplates().py_library(
    cov_level=96,
    microgenerator=True,
    unit_test_python_versions=["3.8", "3.9", "3.10", "3.11", "3.12"],
    versions=gcp.common.detect_versions(path="./google", default_first=True),
)
s.move(
    templated_files,
    excludes=[
        ".coveragerc",
        ".github/release-please.yml",
        "docs/multiprocessing.rst",
        "docs/index.rst",
        "README.rst",
    ],
)


s.replace(
    "noxfile.py",
    """\
BLACK_VERSION = "black\[jupyter\]==23.7.0"
""",
    """\
PYTYPE_VERSION = "pytype==2021.09.09"
BLACK_VERSION = "black[jupyter]==23.7.0"
""",
)
# add pytype to nox.options.sessions
s.replace(
    "noxfile.py",
    """nox.options.sessions = \[
    "unit",""",
    """nox.options.sessions = [
    "unit",
    "pytype", # Custom pytype session""",
)

# add pytype nox session
s.replace(
    "noxfile.py",
    """
@nox.session\(python="3.10"\)
def docfx\(session\):""",
    """
@nox.session(python=DEFAULT_PYTHON_VERSION)
def pytype(session):
    \"\"\"Run type checks.\"\"\"
    constraints_path = str(
        CURRENT_DIRECTORY / "testing" / f"constraints-{session.python}.txt"
    )
    install_unittest_dependencies(session, "-c", constraints_path)
    session.install(PYTYPE_VERSION)
    # See https://github.com/google/pytype/issues/464
    session.run("pytype", "-P", ".", "google/cloud/pubsublite")

@nox.session(python="3.10")
def docfx(session):""",
)

# Remove once issues with pytest-asyncio 0.23.x have been resolved
# https://github.com/pytest-dev/pytest-asyncio/issues?q=is%3Aissue+is%3Aopen+0.23.2+
s.replace("noxfile.py", "\"pytest-asyncio\"", "\"pytest-asyncio<0.23\"")

python.py_samples(skip_readmes=True)

# run format session for all directories which have a noxfile
for noxfile in Path(".").glob("**/noxfile.py"):
    s.shell.run(["nox", "-s", "blacken"], cwd=noxfile.parent, hide_output=False)
