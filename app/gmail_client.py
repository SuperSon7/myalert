import imaplib
import email
import os
import json
from datetime import datetime
from email.header import decode_header

class GoogleAlertClient:
    def __init__(self, email_address, password, save_directory):
        self.email_address = email_address
        self.password = password
        self.save_directory = save_directory
        self.mail = None
        
        # 저장 디렉토리 생성
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
    def connect(self):
        """이메일 서버에 연결"""
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")
        self.mail.login(self.email_address, self.password)
        self.mail.select("INBOX")
        
    def get_today_date(self):
        """오늘 날짜 반환"""
        return datetime.now().strftime("%d-%b-%Y")
        
    def search_for_alert(self):
        """알림 이메일 검색"""
        date_str = self.get_today_date()
        
        status, massage = self.mail.search(None, f'FROM, "alert@google.com" ON "{date_str}"')
        
        if status != "OK":
            print("No messages found!")
            return
        
        # TODO 받아온 메시지 파싱해서 필요 부분만 저장하기
            
