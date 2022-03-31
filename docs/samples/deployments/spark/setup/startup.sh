#!/bin/bash

pip install presidio-analyzer
pip install presidio-anonymizer
pip install azure-storage-blob
python -m spacy download en_core_web_md
python -m spacy download pl_core_news_md