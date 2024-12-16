SCRAPER_DIR=$(realpath $(dirname "${BASH_SOURCE[0]}"))
SCRAPER_ROOT=$SCRAPER_DIR
export SCRAPER_ROOT

poetry lock
poetry install
source $(poetry env info --path)/bin/activate
pre-commit install
echo "Scraper Activated"
