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
    # Work around gapic generator bug: https://github.com/googleapis/gapic-generator-python/issues/902
    s.replace(library / f"google/cloud/pubsublite_{library.name}/types/common.py",
                r""".
    Attributes:""",
                r""".\n
    Attributes:"""
    )

    # Work around gapic generator bug: https://github.com/googleapis/gapic-generator-python/issues/902
    s.replace(library / f"google/cloud/pubsublite_{library.name}/types/common.py",
                r""".
        Attributes:""",
                r""".\n
        Attributes:""",
    )

    # Work around gapic generator bug: https://github.com/googleapis/gapic-generator-python/issues/902
    s.replace(library / f"google/cloud/pubsublite_{library.name}/types/common.py",
                r""".
            Attributes:""",
                r""".\n
            Attributes:""",
    )

    excludes = [
        "docs/pubsublite_v1",  # generated GAPIC docs should be ignored
        "docs/index.rst",
        "google/cloud/pubsublite/__init__.py",
        "README.rst",
        "scripts/fixup*.py",  # new libraries do not need the keyword fixup script
        "setup.py",
    ]
    s.move(library, excludes=excludes)

s.remove_staging_dirs()

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(
python.py_samples(skip_readmes=True)
    cov_level=70,
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


s.shell.run(["nox", "-s", "blacken"], hide_output=False)
