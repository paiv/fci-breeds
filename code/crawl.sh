#!/bin/sh

crawler/crawl_fci.py data
crawler/export_fci.py data/fci/dump fci-breeds.csv
