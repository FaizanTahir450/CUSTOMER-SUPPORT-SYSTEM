# gmail_service.py
import os
import base64
import re
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import Config

logger = logging.getLogger(__name__)

# Scopes needed: read inbox, create drafts, mark as read
# gmail.compose covers draft creation (no send scope needed — nothing is auto-sent)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",  # create drafts
    "https://www.googleapis.com/auth/gmail.modify",   # mark as read
]


class GmailService:
    def __init__(self):
        self.service = None
        self._authenticate()

    # ── Auth ────────────────────────────────────────────────────────────────

    def _authenticate(self):
        """OAuth2 flow: reads token.json if it exists, otherwise opens browser."""
        creds = None

        if os.path.exists(Config.GMAIL_TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(Config.GMAIL_TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(Config.GMAIL_CREDENTIALS_PATH):
                    raise FileNotFoundError(
                        f"Gmail credentials file not found at '{Config.GMAIL_CREDENTIALS_PATH}'. "
                        "Download it from Google Cloud Console → APIs & Services → Credentials."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GMAIL_CREDENTIALS_PATH, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(Config.GMAIL_TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())
            logger.info(f"Gmail token saved to '{Config.GMAIL_TOKEN_PATH}'")

        self.service = build("gmail", "v1", credentials=creds)
        logger.info("Gmail API authenticated successfully")

    # ── Reading ─────────────────────────────────────────────────────────────

    def get_unread_emails(self) -> List[Dict]:
        """
        Returns ALL unread inbox emails ordered oldest-first (true FIFO).

        Gmail API paginates results (max 500 per page). We follow every
        nextPageToken until there are no more pages, collecting all message
        IDs before processing any of them. Reversing the complete list
        guarantees strict FIFO regardless of how many emails are waiting.
        """
        try:
            all_message_refs = []
            page_token = None

            # Paginate through every page of unread messages
            while True:
                kwargs = {
                    "userId":     "me",
                    "labelIds":   ["INBOX", "UNREAD"],
                    "maxResults": 500,   # maximum Gmail allows per page
                }
                if page_token:
                    kwargs["pageToken"] = page_token

                result     = self.service.users().messages().list(**kwargs).execute()
                messages   = result.get("messages", [])
                all_message_refs.extend(messages)

                page_token = result.get("nextPageToken")
                if not page_token:
                    break   # no more pages

            if not all_message_refs:
                return []

            print(f"  📨 Total unread emails found: {len(all_message_refs)}")

            # Gmail returns newest-first — reverse the FULL list for true FIFO
            all_message_refs = list(reversed(all_message_refs))

            emails = []
            for msg_ref in all_message_refs:
                email_data = self._parse_email(msg_ref["id"])
                if email_data:
                    emails.append(email_data)

            return emails

        except HttpError as e:
            logger.error(f"Gmail API error while fetching emails: {e}")
            return []

    def _parse_email(self, message_id: str) -> Optional[Dict]:
        """Fetch and parse a single email by message ID."""
        try:
            msg = self.service.users().messages().get(
                userId="me",
                id=message_id,
                format="full",
            ).execute()

            headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}

            raw_sender   = headers.get("from", "")
            sender_email = self._extract_email(raw_sender)
            sender_name  = self._extract_name(raw_sender)
            subject      = headers.get("subject", "(No Subject)")
            thread_id    = msg.get("threadId", message_id)
            body         = self._extract_body(msg["payload"])

            if not sender_email or not body.strip():
                return None

            return {
                "id":           message_id,
                "thread_id":    thread_id,
                "sender_email": sender_email,
                "sender_name":  sender_name,
                "subject":      subject,
                "body":         body.strip(),
            }

        except HttpError as e:
            logger.error(f"Error parsing email {message_id}: {e}")
            return None

    def _extract_body(self, payload: Dict) -> str:
        """Recursively extract plain-text body from MIME payload."""
        body = ""

        if payload.get("mimeType") == "text/plain":
            data = payload.get("body", {}).get("data", "")
            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        elif payload.get("mimeType") == "text/html" and not body:
            data = payload.get("body", {}).get("data", "")
            if data:
                html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                body = re.sub(r"<[^>]+>", " ", html)
                body = re.sub(r"\s+", " ", body).strip()

        for part in payload.get("parts", []):
            candidate = self._extract_body(part)
            if candidate:
                body = candidate
                break

        return body

    @staticmethod
    def _extract_email(raw: str) -> str:
        match = re.search(r"<([^>]+)>", raw)
        if match:
            return match.group(1).strip().lower()
        return raw.strip().lower()

    @staticmethod
    def _extract_name(raw: str) -> str:
        match = re.search(r"^(.*?)\s*<", raw)
        if match:
            return match.group(1).strip().strip('"')
        return raw.split("@")[0] if "@" in raw else raw

    # ── Draft creation (replaces send) ──────────────────────────────────────

    def create_draft(
        self,
        to_email: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Save the AI-generated reply as a Gmail Draft instead of sending it.

        The draft appears in the Drafts folder of the authenticated Gmail account.
        A human must open Gmail, review/edit the draft, and click Send manually.

        The 'From' is always the authenticated Gmail account — Gmail API does not
        allow sending as a different address unless that address is configured as
        a 'Send As' alias inside Gmail settings.

        Returns the draft ID string on success, or None on failure.
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["To"]      = to_email
            msg["From"]    = "me"   # resolved to the authenticated account by Gmail API
            msg["Subject"] = subject if subject.startswith("Re:") else f"Re: {subject}"

            plain = MIMEText(body, "plain", "utf-8")
            html  = MIMEText(self._build_html_email(body), "html", "utf-8")
            msg.attach(plain)
            msg.attach(html)

            raw     = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
            message = {"raw": raw}
            if thread_id:
                message["threadId"] = thread_id  # keeps it in the same email thread

            draft = self.service.users().drafts().create(
                userId="me",
                body={"message": message},
            ).execute()

            draft_id = draft.get("id")
            logger.info(f"Draft saved → To: {to_email} | Subject: {msg['Subject']}")
            return draft_id

        except HttpError as e:
            logger.error(f"Failed to create draft for {to_email}: {e}")
            return None

    # ── Mark as read ─────────────────────────────────────────────────────────

    def mark_as_read(self, message_id: str) -> None:
        """Remove UNREAD label so we don't process the same email twice."""
        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
        except HttpError as e:
            logger.warning(f"Could not mark email {message_id} as read: {e}")

    # ── HTML template ─────────────────────────────────────────────────────────

    @staticmethod
    def _build_html_email(plain_text: str) -> str:
        formatted = plain_text.replace("\n", "<br>")
        return f"""
        <html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto;padding:20px;">
            <div style="border-bottom:2px solid #4A90D9;padding-bottom:10px;margin-bottom:20px;">
                <h2 style="color:#4A90D9;margin:0;">Lama Retail — Customer Support</h2>
                <p style="margin:4px 0;color:#888;font-size:13px;">Sophia | Support Agent</p>
            </div>
            <div style="line-height:1.7;font-size:15px;">
                {formatted}
            </div>
            <div style="border-top:1px solid #eee;margin-top:30px;padding-top:10px;font-size:12px;color:#aaa;">
                This email was prepared by Lama Retail's automated support system.
            </div>
        </body></html>
        """