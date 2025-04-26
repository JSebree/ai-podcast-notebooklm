import os, datetime, json
from google.oauth2 import service_account          # ← add this
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",   # <— add Drive scope
]
CREDS_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT")
creds = service_account.Credentials.from_service_account_info(
    json.loads(CREDS_JSON), scopes=SCOPES
)

docs_service  = build("docs",  "v1", credentials=creds, cache_discovery=False)
drive_service = build("drive", "v3", credentials=creds, cache_discovery=False)

def create_daily_doc(stories: list[dict]) -> str:
    today = datetime.datetime.now().strftime("%B %d, %Y")
    title = f"Emerging Tech Digest – {today}"

    # 1️⃣  create the Doc in the service-account's My Drive
    try:
        doc = docs_service.documents().create(body={"title": title}).execute()
    except Exception as err:
        import traceback, sys
        print("[DEBUG] Docs API error:", err, file=sys.stderr)
        traceback.print_exc()                # full stack trace
        raise                                 # stop the run so you see red
    doc_id = doc["documentId"]
    print("[DEBUG] Created Doc →", doc_id)

    # 2️⃣  move it into the user-defined folder
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if folder_id:
        # fetch current parents so we can remove them
        meta = drive_service.files().get(
            fileId=doc_id, fields="parents"
        ).execute()
        previous_parents = ",".join(meta.get("parents", []))
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields="id, parents",
        ).execute()
        print("[DEBUG] Moved Doc; new parents →", res.get("parents"))

    # … (continue with your batchUpdate text insertion) …
    return f"https://docs.google.com/document/d/{doc_id}"
