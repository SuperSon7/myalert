import os
from dotenv import load_dotenv

load_dotenv()

CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "./credentials/credentials.json")
TOKEN_FILE = os.getenv("TOKEN_FILE", "./credentials/token.json")
GMAIL_USER = os.getenv("GMAIL_USER","")

# Alerts 설정 언제 읽을 건지..
ALERTS_QUERY="from:googlealerts-noreply@google.com AND after:"

STORAGE_DIR = os.getenv("STORAGE_DIR", "./data")

# IF you want modify this please delete file token.json
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]