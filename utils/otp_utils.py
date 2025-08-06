# otp_utils.py
import imaplib
import email
import re
import time
from datetime import datetime, timedelta

def get_otp_from_gmail(email_address: str, password: str, valid_senders: list, keyword=None):
    """
    Extract OTP from the latest 10 emails in Gmail inbox.

    Args:
        email_address (str): Gmail address.
        password (str): App password for Gmail.
        valid_senders (list): List of allowed sender emails.
        keyword (str, optional): Keyword to match in subject/body.

    Returns:
        str: OTP if found, else None.
    """
    print(f"\n📧 Reading OTP for: {email_address} at {datetime.now().strftime('%c')}")
    mail = None
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_address, password)
        mail.select("inbox")

        # Get ALL emails (not just unread)
        status, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()

        if not mail_ids:
            print("📭 No emails found in inbox.")
            return None

        latest_10_ids = mail_ids[-10:]  # Get last 10 emails
        print(f"📬 Checking last {len(latest_10_ids)} emails")

        for i in reversed(latest_10_ids):  # Start from most recent
            status, msg_data = mail.fetch(i, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            if not msg:
                continue

            from_address = email.utils.parseaddr(msg.get("From"))[1]
            subject = msg.get("Subject", "")
            print(f"📨 From: {from_address}, Subject: {subject}")

            if from_address not in valid_senders:
                print(f"⚠️ Sender {from_address} not in valid senders: {valid_senders}")
                continue
            if keyword and keyword.lower() not in subject.lower():
                print(f"⚠️ Keyword '{keyword}' not found in subject: {subject}")
                continue

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain' and 'attachment' not in str(part.get('Content-Disposition')):
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            otp_match = re.search(r'\b\d{6}\b', body)
            if otp_match:
                otp = otp_match.group(0)
                print(f"✅ OTP Found: {otp}")
                mail.logout()
                return otp

        print("⚠️ No valid OTP found in last 10 emails.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if mail:
            try:
                mail.logout()
            except Exception as e:
                print(f"❗ Logout Error: {e}")
    return None
