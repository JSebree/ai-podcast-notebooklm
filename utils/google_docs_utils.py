import os, datetime, json, re, sys, logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── logging setup ───────────────────────────────────────────────
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

# ── load service-account creds ─────────────────────────────────
sa_json_b64 = os.getenv("GOOGLE_SERVICE_ACCOUNT")
if not sa_json_b64:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT env var is empty.")
try:
    creds = service_account.Credentials.from_service_account_info(
        json.loads(sa_json_b64), scopes=SCOPES
    )
except json.JSONDecodeError as err:
    raise ValueError("GOOGLE_SERVICE_ACCOUNT contains invalid JSON") from err

docs_service  = build("docs",  "v1", credentials=creds, cache_discovery=False)
drive_service = build("drive", "v3", credentials=creds, cache_discovery=False)


def create_daily_doc(stories: list[dict]) -> str:
    """Create the Google Doc, move it to the folder, share, and return its URL."""
    today = datetime.datetime.now().strftime("%B %d, %Y")
    title = f"Emerging Tech Digest – {today}"

    # 1️⃣  Create Doc
    print("[DEBUG] Creating Google Doc titled:", title, file=sys.stderr)
    try:
        doc = docs_service.documents().create(body={"title": title}).execute()
    except Exception as err:
        logger.error("Docs API create failed: %s", err)
        raise
    doc_id = doc["documentId"]
    print("[DEBUG] Created Doc →", doc_id, file=sys.stderr)

    # 2️⃣  Move into folder (if provided)
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if folder_id:
        print("[DEBUG] Moving Doc into folder:", folder_id, file=sys.stderr)
        try:
            prev = drive_service.files().get(fileId=doc_id, fields="parents").execute()
            drive_service.files().update(
                fileId=doc_id,
                addParents=folder_id,
                removeParents=",".join(prev.get("parents", [])),
                fields="id, parents",
            ).execute()
            print("[DEBUG] Moved Doc; new parents →", folder_id, file=sys.stderr)
        except Exception as err:
            logger.error("Drive API move failed: %s", err)
            raise
    else:
        print("[DEBUG] GOOGLE_DRIVE_FOLDER_ID not set – skipping move.", file=sys.stderr)

    # 3️⃣  Optional share with your Gmail
    share_email = os.getenv("SHARE_WITH_EMAIL")
    if share_email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", share_email):
            raise ValueError(f"SHARE_WITH_EMAIL is invalid: {share_email}")

        print("[DEBUG] Sharing Doc with", share_email, file=sys.stderr)
        try:
            drive_service.permissions().create(
                fileId=doc_id,
                body={"type": "user", "role": "writer", "emailAddress": share_email},
                sendNotificationEmail=False,
            ).execute()
            print("[DEBUG] Shared Doc with", share_email, file=sys.stderr)
        except Exception as err:
            logger.error("Drive API share failed: %s", err)
            # share failure isn’t fatal; continue

    # 4️⃣  Return the public link
    return f"https://docs.google.com/document/d/{doc_id}"
