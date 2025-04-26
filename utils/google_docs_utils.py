import os, datetime, json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/documents"]
CREDS_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT")
creds = service_account.Credentials.from_service_account_info(
    json.loads(CREDS_JSON), scopes=SCOPES)

docs_service = build("docs", "v1", credentials=creds, cache_discovery=False)

def create_daily_doc(stories):
    today = datetime.datetime.now().strftime("%B %d, %Y")
    title = f"Emerging Tech Digest – {today}"
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    requests_payload = []
    for idx,s in enumerate(stories, start=1):
        requests_payload.extend([
            {"insertText":{"location":{"index":1},"text":f"\n\n### {idx}. {s['headline']}\n"}},
            {"insertText":{"location":{"index":1},"text":f"*Podcast Title:* **{s['podcast_title']}**\n"}},
            {"insertText":{"location":{"index":1},"text":s['summary']+"\n"}},
            {"insertText":{"location":{"index":1},"text":"Supporting Resources:\n"}},
        ])
        for link in s["links"]:
            requests_payload.append({"insertText":{"location":{"index":1},"text":f"- {link}\n"}})

    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests_payload}).execute()
    return f"https://docs.google.com/document/d/{doc_id}"
