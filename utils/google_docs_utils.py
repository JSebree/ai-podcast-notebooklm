import os
import datetime
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

# Load and validate service account credentials
service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT")
if not service_account_info:
    raise EnvironmentError("Environment variable 'GOOGLE_SERVICE_ACCOUNT' is not set or empty.")
try:
    creds = service_account.Credentials.from_service_account_info(
        json.loads(service_account_info), scopes=SCOPES
    )
except json.JSONDecodeError as e:
    raise ValueError("Invalid JSON in 'GOOGLE_SERVICE_ACCOUNT':") from e

docs_service = build("docs", "v1", credentials=creds, cache_discovery=False)
drive_service = build("drive", "v3", credentials=creds, cache_discovery=False)


def create_daily_doc(stories: list[dict]) -> str:
    today = datetime.datetime.now().strftime("%B %d, %Y")
    title = f"Emerging Tech Digest – {today}"

    # 1️⃣ Create Google Doc
    try:
        doc = docs_service.documents().create(body={"title": title}).execute()
    except Exception as err:
        raise RuntimeError("Failed to create Google Document") from err

    doc_id = doc["documentId"]
    logger.debug("Created Doc → %s", doc_id)

    # 2️⃣ Move to specified folder
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if folder_id:
        try:
            prev = drive_service.files().get(fileId=doc_id, fields="parents").execute()
            drive_service.files().update(
                fileId=doc_id,
                addParents=folder_id,
                removeParents=",".join(prev.get("parents", [])),
                fields="id, parents",
            ).execute()
            logger.debug("Moved Doc; new parents → %s", folder_id)
        except Exception as err:
            raise RuntimeError("Failed to move Google Document to folder") from err
    else:
        logger.debug("Folder ID not set. Skipping move step.")

    # 3️⃣ Optional direct share
    share_email = os.getenv("SHARE_WITH_EMAIL")
    if share_email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", share_email):
            raise

