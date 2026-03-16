# 🔗 Salesforce Bulk API 2.0: CSV Data Loader

![Integration](https://img.shields.io/badge/Salesforce-Integration-00A1E0?style=flat&logo=salesforce&logoColor=white) ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)

> **Category**: Salesforce Integration

## Overview

A Python script using the Salesforce Bulk API 2.0 to efficiently load large CSV datasets into any Salesforce object. Supports insert, update, upsert, and delete operations with progress tracking and error reporting.

## Files

```
2026-03-16-sf-bulk-api-data-loader/
├── `.env.example`
├── `requirements.txt`
├── `sample_leads.csv`
├── `sf_bulk_loader.py`
```

## Code Preview

```python
"""
Salesforce Bulk API 2.0 Data Loader
=====================================
Loads CSV data into Salesforce using Bulk API 2.0.
Supports: insert, update, upsert, delete

Requirements:
    pip install simple-salesforce python-dotenv

Usage:
    python sf_bulk_loader.py --file leads.csv --object Lead --operation insert
    python sf_bulk_loader.py --file accounts.csv --object Account --operation upsert --external-id External_Id__c
"""
import os
import csv
import json
import time
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 5


def get_sf_client() -> Salesforce:
    return Salesforce(
        username=os.environ["SF_USERNAME"],
        password=os.environ["SF_PASSWORD"],
        security_token=os.environ["SF_SECURITY_TOKEN"],
        domain=os.environ.get("SF_DOMAIN", "login"),
    )


def read_csv(filepath: str) -> str:
// ... (see full file)
```

## About

This project is part of [apex-lab](https://github.com/selvavp-hub/apex-lab) —
a daily series of real Salesforce & AI code projects demonstrating
Apex development, LWC, integrations, and applied AI.

---
*Generated as part of the daily Salesforce coding series.*
