# Bash script to ingest data
# This involves scraping the data from the web and then cleaning up and putting in FAISS file.
# Error if any command fails
set -e
python3 ingest.py
