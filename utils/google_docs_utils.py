import os, base64, json, datetime, re, sys, logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── logging setup ──────────────────────────────────────────────
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

# ── load + decode service-account creds ────────────────────────
sa_b64 = os.getenv("GOOGLE_SERVICE_ACCOUNT")
if not sa_b64:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT env var is empty.")

try:
    sa_info = json.loads(base64.b64decode(sa_b64).decode("utf-8"))
except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as err:
    raise ValueError("GOOGLE_SERVICE_ACCOUNT secret must be base64-encoded JSON") from err

creds = service_account.Credentials.from_service_account_info(sa_info, scopes=SCOPES)

docs_service  = build("docs",  "v1", credentials=creds, cache_discovery=False)
drive_service = build("drive", "v3", credentials=creds, cache_discovery=False)

# ── helper ─────────────────────────────────────────────────────
def _debug(msg, *vals):
    print("[DEBUG]", msg, *vals, file=sys.stderr)

# ── main function ──────────────────────────────────────────────
def create_daily_doc(stories: list[dict]) -> str:
    """Create the Google Doc, move it, share it, and return its URL."""
    today = datetime.datetime.now().strftime("%B %d, %Y")
    title = f"Emerging Tech Digest – {today}"

    # 1️⃣  create doc
    _debug("Creating Google Doc titled:", title)
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    _debug("Created Doc →", doc_id)

    # 2️⃣  move into folder
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if folder_id:
        _debug("Moving Doc into folder:", folder_id)
        prev = drive_service.files().get(fileId=doc_id, fields="parents").execute()
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=",".join(prev.get("parents", [])),
            fields="id, parents",
            supportsAllDrives=True,
        ).execute()
        _debug("Moved Doc; new parents →", folder_id)
    else:
        _debug("GOOGLE_DRIVE_FOLDER_ID not set – skipping move.")

    # 3️⃣  optional share with your Gmail
    share_email = os.getenv("SHARE_WITH_EMAIL")
    if share_email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", share_email):
            raise ValueError(f"SHARE_WITH_EMAIL is invalid: {share_email}")

        _debug("Sharing Doc with", share_email)
        drive_service.permissions().create(
            fileId=doc_id,
            body={"type": "user", "role": "writer", "emailAddress": share_email},
            sendNotificationEmail=False,
        ).execute()
        _debug("Shared Doc with", share_email)

    # 4️⃣  return link
    return f"https://docs.google.com/document/d/{doc_id}"
