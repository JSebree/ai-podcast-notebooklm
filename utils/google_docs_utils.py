import os, datetime, json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

creds = service_account.Credentials.from_service_account_info(
    json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT")), scopes=SCOPES
)

docs_service  = build("docs",  "v1", credentials=creds, cache_discovery=False)
drive_service = build("drive", "v3", credentials=creds, cache_discovery=False)

def create_daily_doc(stories: list[dict]) -> str:
    today = datetime.datetime.now().strftime("%B %d, %Y")
    title = f"Emerging Tech Digest – {today}"

    # 1️⃣ create doc
    try:
        doc = docs_service.documents().create(body={"title": title}).execute()
    except Exception as err:
        print("[DEBUG] Docs API error:", err)
        raise
    doc_id = doc["documentId"]
    print("[DEBUG] Created Doc →", doc_id)

    # 2️⃣ move to specified folder
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
            print("[DEBUG] Moved Doc; new parents →", folder_id)
        except Exception as err:
            print("[DEBUG] Move error:", err)
            raise

    # 3️⃣ optional direct share
    share_email = os.getenv("SHARE_WITH_EMAIL")
    if share_email:
        try:
            drive_service.permissions().create(
                fileId=doc_id,
                body={"type": "user", "role": "writer", "emailAddress": share_email},
                sendNotificationEmail=False,
            ).execute()
            print("[DEBUG] Shared Doc with", share_email)
        except Exception as err:
            print("[DEBUG] Share error:", err)

    # 4️⃣ now insert content (placeholder)
    # ... your batchUpdate requests here ...

    return f"https://docs.google.com/document/d/{doc_id}"
