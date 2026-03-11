# poller.py
import threading
import traceback
from typing import Optional
import logging

from sqlalchemy import text

from app.services.email.gmail import GmailService
from app.services.memory import LLMCustomerSupportMemory
from app.models.database import get_db_service
from app.config import Config

logger = logging.getLogger(__name__)

UNREGISTERED_TEMPLATE = """Hello,

Thank you for reaching out to Lama Retail's customer support.

Unfortunately, we could not find an account associated with this email address ({sender_email}).

To access support, please ensure you are writing from the email address you used during registration on our website. If you haven't registered yet, you can create an account at our website.

If you believe this is an error, please contact us through the live chat on our website.

Warm regards,
Sophia
Lama Retail Customer Support"""


class EmailPoller:
    """
    Background thread that:
    1. Polls Gmail inbox for unread emails at a configurable interval.
    2. Looks up the sender's gmail_id in the users table.
    3. If found  → runs through support graph and saves reply as a draft.
    4. If not found → sends the unregistered-user template immediately.
    5. Marks the email as read so it is never processed twice.
    """

    def __init__(self, support_graph):
        self.support_graph = support_graph
        self.gmail_service: Optional[GmailService] = None   # lazy-init in thread
        self.mysql_service = get_db_service()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self):
        """Start the polling thread."""
        self._thread = threading.Thread(
            target=self._poll_loop,
            name="EmailPoller",
            daemon=True,          # dies automatically when main process exits
        )
        self._thread.start()
        logger.info(f"Email poller started (interval: {Config.GMAIL_POLL_INTERVAL}s)")

    def stop(self):
        """Signal the polling thread to stop."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("Email poller stopped")

    # ── Internal loop ─────────────────────────────────────────────────────

    def _poll_loop(self):
        # Authenticate Gmail inside the thread (browser prompt happens here on first run)
        try:
            self.gmail_service = GmailService()
        except Exception as e:
            logger.error(f"Gmail authentication failed — email poller will not run: {e}")
            return

        while not self._stop_event.is_set():
            try:
                self._process_unread_emails()
            except Exception:
                logger.error("Unexpected error in email poller:")
                logger.error(traceback.format_exc())

            # Wait for next poll, but wake up immediately if stop() is called
            self._stop_event.wait(timeout=Config.GMAIL_POLL_INTERVAL)

    def _process_unread_emails(self):
        emails = self.gmail_service.get_unread_emails()
        if not emails:
            return

        logger.info(f"Found {len(emails)} unread email(s)")

        for email in emails:
            try:
                self._handle_single_email(email)
            except Exception:
                logger.error(f"Error handling email {email.get('id')}:")
                logger.error(traceback.format_exc())
            finally:
                # Always mark as read — even on error — to avoid infinite retry loops
                self.gmail_service.mark_as_read(email["id"])

    # ── Per-email logic ───────────────────────────────────────────────────────

    def _handle_single_email(self, email: dict):
        sender_email = email["sender_email"]
        subject      = email["subject"]
        body         = email["body"]
        thread_id    = email["thread_id"]

        logger.info(f"Processing email from: {sender_email} | Subject: {subject}")

        # 1. Look up user by gmail_id
        user_id = self._find_user_by_gmail(sender_email)

        if not user_id:
            # Not a registered user → send rejection notice
            logger.warning(f"Email {sender_email} not registered — sending rejection")
            self.gmail_service.create_draft(
                to_email  = sender_email,
                subject   = subject,
                body      = UNREGISTERED_TEMPLATE.format(sender_email=sender_email),
                thread_id = thread_id,
            )
            return

        # 2. Registered user → run through support graph
        logger.info(f"Matched user_id='{user_id}' for gmail_id='{sender_email}'")
        response_text = self._run_support_graph(user_id=user_id, message=body)

        # 3. Save the reply as a draft for human review
        draft_id = self.gmail_service.create_draft(
            to_email  = sender_email,
            subject   = subject,
            body      = response_text,
            thread_id = thread_id,
        )

        if draft_id:
            logger.info(f"Draft saved for human review (draft_id={draft_id}) → {sender_email}")
        else:
            logger.error(f"Draft creation failed for {sender_email}")

    def _find_user_by_gmail(self, gmail_id: str) -> Optional[str]:
        """Return user_id for the given gmail_id, or None if not found."""
        try:
            with self.mysql_service.engine.connect() as conn:
                row = conn.execute(
                    text("SELECT user_id FROM users WHERE gmail_id = :gid LIMIT 1"),
                    {"gid": gmail_id},
                ).fetchone()
            return str(row[0]) if row else None
        except Exception as e:
            logger.error(f"DB lookup error for gmail_id '{gmail_id}': {e}")
            return None

    def _run_support_graph(self, user_id: str, message: str) -> str:
        """Load memory, invoke the support graph, return the response string."""
        try:
            memory = LLMCustomerSupportMemory(
                mysql_service=self.mysql_service,
                user_id=user_id,
            )
            memory.load_from_db()

            # Get conversation history for context
            conversation_history = memory.get_conversation_history()

            result = self.support_graph.invoke({
                "user_id":              user_id,
                "message":              message,
                "response":             "",
                "classification":       "",
                "sub_classification":   "",
                "context":              "",
                "memory":               memory,
                "conversation_history": conversation_history,
            })

            logger.info(f"Support graph response generated for user '{user_id}'")
            return result.get("response", "I'm sorry, I couldn't process your request.")

        except Exception as e:
            logger.error(f"Support graph error for user '{user_id}': {e}")
            return (
                "I'm sorry, I encountered an issue processing your request. "
                "Please try again or contact us through our website chat."
            )
