export GOOGLE_CLOUD_PROJECT_NUMBER=502009289245
export INSTALL_LIBRARY_FROM_SOURCE=True

cd ./samples/snippets

python3.6 -m pip install --quiet nox-automation
python3.6 -m pip install --upgrade --quiet nox
python3.6 -m nox
