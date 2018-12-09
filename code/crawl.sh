#!/bin/sh

crawler/crawl_fci.py --data-dir data
crawler/export_fci.py --data-dir data/fci/dump fci-breeds.csv
