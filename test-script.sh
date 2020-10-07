DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT=$( dirname "$DIR" )

cd $DIR

python3.6 -m pip install --quiet nox-automation
python3.6 -m pip install --upgrade --quiet nox

python3.6 -m nox

cd ./samples/snippets

export GOOGLE_CLOUD_PROJECT_NUMBER=502009289245
export INSTALL_LIBRARY_FROM_SOURCE=True

for file in samples/**/noxfile.py; do
    python3.6 -m nox
done