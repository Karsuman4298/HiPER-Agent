import os
import pywhatkit
from typing import Optional, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class PluginLayer:
    def __init__(self):
        # Load environment variables for credentials
        self.whatsapp_enabled = True # Always try, relies on browser
        self.gmail_user = os.getenv("GMAIL_USER")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.twitter_api_key = os.getenv("TWITTER_API_KEY")
        self.contacts_file = "contacts.json"

    def resolve_contact(self, name: str) -> str:
        """Resolves a name into a phone number or email from contacts.json."""
        import json
        if not os.path.exists(self.contacts_file):
            return name # Return original if no file
            
        try:
            with open(self.contacts_file, "r") as f:
                contacts = json.load(f)
            # Case-insensitive search
            for k, v in contacts.items():
                if k.lower() == name.lower():
                    return v
        except Exception:
            pass
        return name # Default to original if not found

    def send_whatsapp(self, phone_number: str, message: str) -> str:
        """Sends a WhatsApp message via pywhatkit (requires browser login)."""
        try:
            # Note: This opens a browser tab
            pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=15, tab_close=True)
            return f"WhatsApp message scheduled/sent to {phone_number}."
        except Exception as e:
            return f"Error sending WhatsApp: {str(e)}"

    def send_email(self, to_email: str, subject: str, body: str) -> str:
        """Sends an email via Gmail SMTP using App Passwords."""
        if not self.gmail_user or not self.gmail_password:
            return "Error: GMAIL_USER or GMAIL_APP_PASSWORD not set in .env"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            return f"Email successfully sent to {to_email}."
        except Exception as e:
            return f"Error sending email: {str(e)}"

    def check_emails(self, limit: int = 5) -> str:
        """Reads recent emails from Gmail via IMAP."""
        if not self.gmail_user or not self.gmail_password:
            return "Error: GMAIL_USER or GMAIL_APP_PASSWORD not set in .env"
        
        try:
            import imaplib
            import email
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_user, self.gmail_password)
            mail.select('inbox')
            
            status, data = mail.search(None, 'ALL')
            mail_ids = data[0].split()
            recent_ids = mail_ids[-limit:]
            
            summary = f"Found {len(recent_ids)} recent emails:\n"
            for m_id in recent_ids:
                status, data = mail.fetch(m_id, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                summary += f"From: {msg['from']}\nSubject: {msg['subject']}\n---\n"
            
            mail.logout()
            return summary
        except Exception as e:
            return f"Error reading emails: {str(e)}"

    def send_tweet(self, text: str) -> str:
        """Posts a tweet via Tweepy."""
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        if not self.twitter_api_key or not access_token:
            return "Error: Twitter API keys/tokens not set in .env"
        
        try:
            import tweepy
            # V2 Client
            client = tweepy.Client(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
                consumer_key=self.twitter_api_key,
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=access_token,
                access_token_secret=access_secret
            )
            response = client.create_tweet(text=text)
            return f"Tweet posted! ID: {response.data['id']}"
        except Exception as e:
            return f"Error posting tweet: {str(e)}"

    def send_telegram(self, chat_id: str, message: str) -> str:
        """Sends a message via Telegram Bot API."""
        if not self.telegram_token:
            return "Error: TELEGRAM_BOT_TOKEN not set in .env"
        try:
            import requests # Using simple requests for speed
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": message}
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return f"Telegram message sent to {chat_id}."
            else:
                return f"Error sending Telegram: {response.text}"
        except Exception as e:
            return f"Error: {str(e)}"

# Singleton plugin instance
plugins = PluginLayer()
