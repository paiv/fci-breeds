
# Usage

Install dependencies
```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Collect data
```sh
crawler/crawl_fci.py --data-dir data
crawler/export_fci.py --data-dir data/fci/dump fci-breeds.csv
```

This will download to `data` dir, and compile `fci-breeds.csv`.
