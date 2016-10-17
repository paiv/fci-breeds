#!/bin/sh

virtualenv -p python2.7 .env
. activate
pip install -r requirements.txt

