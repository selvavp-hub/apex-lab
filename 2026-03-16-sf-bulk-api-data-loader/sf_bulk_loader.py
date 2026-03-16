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
    """Read CSV file and return as string for Bulk API upload."""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return f.read()


def create_bulk_job(sf: Salesforce, sf_object: str, operation: str, external_id: str = None) -> str:
    """Create a Bulk API 2.0 ingest job and return the job ID."""
    payload = {
        "object": sf_object,
        "operation": operation.lower(),
        "contentType": "CSV",
        "lineEnding": "LF",
    }
    if operation.lower() == "upsert" and external_id:
        payload["externalIdFieldName"] = external_id

    result = sf.restful("jobs/ingest", method="POST", json=payload)
    job_id = result["id"]
    log.info(f"Created Bulk job: {job_id} | {operation.upper()} {sf_object}")
    return job_id


def upload_csv_data(sf: Salesforce, job_id: str, csv_data: str) -> None:
    """Upload CSV data to the Bulk job."""
    sf.restful(
        f"jobs/ingest/{job_id}/batches",
        method="PUT",
        data=csv_data.encode("utf-8"),
        additional_headers={"Content-Type": "text/csv"},
    )
    log.info(f"Uploaded CSV data ({len(csv_data.encode())/1024:.1f} KB)")


def close_job(sf: Salesforce, job_id: str) -> None:
    """Signal that upload is complete and processing should start."""
    sf.restful(f"jobs/ingest/{job_id}", method="PATCH", json={"state": "UploadComplete"})
    log.info("Job closed — Salesforce processing started")


def poll_job(sf: Salesforce, job_id: str) -> dict:
    """Poll the job until it completes and return the final status."""
    while True:
        status = sf.restful(f"jobs/ingest/{job_id}", method="GET")
        state = status["state"]
        log.info(f"Job state: {state}")

        if state in ("JobComplete", "Failed", "Aborted"):
            return status

        time.sleep(POLL_INTERVAL_SECONDS)


def download_results(sf: Salesforce, job_id: str, output_dir: str) -> None:
    """Download successful and failed result files."""
    for result_type in ("successfulResults", "failedResults", "unprocessedrecords"):
        try:
            data = sf.restful(f"jobs/ingest/{job_id}/{result_type}", method="GET")
            filepath = Path(output_dir) / f"{job_id}_{result_type}.csv"
            with open(filepath, "w") as f:
                f.write(str(data))
            log.info(f"Saved {result_type} → {filepath}")
        except Exception as e:
            log.debug(f"Could not download {result_type}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Salesforce Bulk API 2.0 Data Loader")
    parser.add_argument("--file",        required=True, help="Path to CSV file")
    parser.add_argument("--object",      required=True, help="Salesforce object (e.g., Lead, Account)")
    parser.add_argument("--operation",   required=True, choices=["insert", "update", "upsert", "delete"])
    parser.add_argument("--external-id", help="External ID field for upsert")
    parser.add_argument("--output-dir",  default="./results", help="Directory for result files")
    args = parser.parse_args()

    # Validate
    if args.operation == "upsert" and not args.external_id:
        parser.error("--external-id is required for upsert operations")

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    log.info(f"Connecting to Salesforce...")
    sf = get_sf_client()

    log.info(f"Reading CSV: {args.file}")
    csv_data = read_csv(args.file)
    row_count = csv_data.count("\n") - 1  # subtract header
    log.info(f"Rows to process: {row_count:,}")

    # Execute Bulk job
    job_id = create_bulk_job(sf, args.object, args.operation, args.external_id)
    upload_csv_data(sf, job_id, csv_data)
    close_job(sf, job_id)
    status = poll_job(sf, job_id)

    # Results
    log.info("=" * 50)
    log.info(f"Job completed: {status['state']}")
    log.info(f"Records processed: {status.get('numberRecordsProcessed', 0):,}")
    log.info(f"Records failed:    {status.get('numberRecordsFailed', 0):,}")

    download_results(sf, job_id, args.output_dir)


if __name__ == "__main__":
    main()
