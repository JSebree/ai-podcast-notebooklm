import os, base64, json, datetime, re, sys, logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── logging setup ─────────────────────────────────────────────
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def _debug(*msg):
    print("[DEBUG]", *msg, file=sys.stderr)

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

# ── load credentials (raw JSON or base64) ────────────────────────
sa_env = os.getenv("GOOGLE_SERVICE_ACCOUNT")
if not sa_env:
    raise EnvironmentError("GOOGLE_SERVICE_ACCOUNT secret is empty.")

sa_info = None
try:
    decoded = base64.b64decode(sa_env).decode("utf-8")
    if decoded.lstrip().startswith("{"):
        sa_info = json.loads(decoded)
        _debug("Service-account secret detected as base64 JSON.")
except Exception:
    pass

if sa_info is None:
    try:
        sa_info = json.loads(sa_env)
        _debug("Service-account secret detected as raw JSON.")
    except json.JSONDecodeError as err:
        raise ValueError(
            "GOOGLE_SERVICE_ACCOUNT secret is neither base64 nor valid JSON."
        ) from err

creds = service_account.Credentials.from_service_account_info(sa_info, scopes=SCOPES)
docs_service  = build("docs",  "v1", credentials=creds, cache_discovery=False)
drive_service = build("drive", "v3", credentials=creds, cache_discovery=False)

# ── main function ───────────────────────────────────────────────
def create_daily_doc(stories: list[dict]) -> str:
    """Create the Google Doc, populate with content, move it, share it, and return its URL."""
    today = datetime.datetime.now().strftime("%B %d, %Y")
    title = f"Emerging Tech Digest – {today}"

    # 1️⃣ Create the empty doc
    _debug("Creating Google Doc titled:", title)
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    _debug("Created Doc →", doc_id)

    # 2️⃣ Populate content via batchUpdate
    # Fetch current doc to find insert location
    doc_content = docs_service.documents().get(documentId=doc_id).execute()
    # Initial body.content has one empty paragraph at index 1
    insert_index = 1
    requests = []
    for story in stories:
        # Build the text block for each story
        block = []
        block.append(f"**{story.get('headline', '')}**\n")
        date = story.get('date')
        if date:
            block.append(f"Date: {date}\n")
        summary = story.get('summary', '')
        if summary:
            block.append(f"{summary}\n")
        podcast = story.get('podcast_title')
        if podcast:
            block.append(f"Podcast Title: {podcast}\n")
        links = story.get('links', [])
        if links:
            block.append("Links:\n")
            for link in links:
                block.append(f"- {link}\n")
        block.append("\n")
        text = ''.join(block)
        requests.append({
            'insertText': {
                'location': {'index': insert_index},
                'text': text
            }
        })
        insert_index += len(text)

    if requests:
        _debug("Inserting content for", len(requests), "stories")
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        _debug("Content insertion complete.")
    else:
        _debug("No stories to insert.")

    # 3️⃣ Move into folder
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if folder_id:
        _debug("Moving Doc into folder:", folder_id)
        prev = drive_service.files().get(fileId=doc_id, fields="parents").execute()
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=','.join(prev.get('parents', [])),
            fields="id, parents",
            supportsAllDrives=True
        ).execute()
        _debug("Moved Doc; new parents →", folder_id)
    else:
        _debug("GOOGLE_DRIVE_FOLDER_ID not set – skipping move.")

    # 4️⃣ Optional share
    share_email = os.getenv("SHARE_WITH_EMAIL")
    if share_email:
        _debug("Sharing Doc with", share_email)
        drive_service.permissions().create(
            fileId=doc_id,
            body={'type': 'user', 'role': 'writer', 'emailAddress': share_email},
            sendNotificationEmail=False
        ).execute()
        _debug("Shared Doc with", share_email)

    # 5️⃣ Return the doc URL
    return f"https://docs.google.com/document/d/{doc_id}"
