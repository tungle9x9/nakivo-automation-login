"""
CSV and JSON test data loader converting records into UserCredential domain models.
"""
import csv
import os
from nakivo_automation_platform.models.user_credential import UserCredential

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def load_csv_credentials(filename="test_data.csv"):
    """Parse CSV rows into UserCredential models."""
    file_path = os.path.join(DATA_DIR, filename)
    credentials = []
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pwd = row["password"]
            if row["scenario"] == "valid_admin" and not pwd:
                pwd = os.getenv("NAKIVO_PASSWORD", "")

            credentials.append(
                UserCredential(
                    username=row["email"],
                    password=pwd,
                    scenario=row["scenario"],
                    expected_success=row["expected_success"].strip().lower() in ("true", "1"),
                    expected_error=row.get("expected_error_contains", ""),
                    description=row.get("description", "")
                )
            )
    return credentials
