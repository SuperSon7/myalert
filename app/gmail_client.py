import imaplib
import os
import logging
import base64
from datetime import datetime
from typing import List,Dict,Any,Optional
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES, ALERTS_QUERY


logger = logging.getLogger(__name__)
class GoogleAlertClient:
    def __init__(self):
        self._service = self._get_gmail_service()

    def get_gmail_service(self):    
        """Gmail Api 서비스객체 반환"""
        creds = None
        
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())      
        return build('gmail','v1',credentials=creds)
    
    def fetch_google_alerts(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        구글 알리미 이메일 가져와 저장하기

        Args:
            max_results (int, optional): 가져올 최대 이메일 수

        Returns:
            가져온 목록
        """        
        
        logger.info(f"구글 알리미 이메일 확인 중...")
        
        date_str = datetime.now().strftime("%Y/%m/%d")
        
        try:
            results = self._service.user().message().list(
                userId='me',
                q=f"{ALERTS_QUERY}{date_str}",
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("구글 알리미 이메일이 없습니다.")
                return []
            
            alerts = []
            for message in messages:
                msg_id = message['id']
                alert = self._process_message(msg_id)
                if alert : 
                    alerts.append(alert)
            
            return alerts
        
        except Exception as e:
            logger.error(f"이메일을 가져오는 중 오류 발생: {e}")
            return []
        # TODO 받아온 메시지 파싱해서 필요 부분만 저장하기
    def _process_message(self, msg_id: str) -> Optioanl[Dict[str, Any]]:
        """
        이메일 메시지 처리
        
        Args:
            msg_id (str): 이메일 메시지 ID

        Returns:
            처리된 알림 or None
        """
        try:
            #이메일 가져오기
            message = self._service.users().messages().get(
                userId='me', id=msg_id, format='full'
            ).execute()
            
            # 제목 필요 없을듯
            # haeders = message['payload']['headers']
            # subejct = next((h['value']))
            
            # 날짜도 필요 없을듯
            
            # 본문 추출
            body = self.get._get_message_body(message)
            if not body:
                logger.warning(f"메시지 {msg_id}에서 본문을 추출할 수 없습니다.")
                return None

            # TODO 파일 어떤식으로 받아와서 파싱 할지 결정
        #     alert_items = self._parse_alert_html(body)
            
        #     return {
        #         'id':msg_id,
        #         'items':alert_items
        #     }
            
        # except Exception as e:
        #     logger.error(f"메시지 {msg_id} 처리 중 오류 발생: {e}")
        #     return None
        
        # def _get_message_body(self, message: Dict[str, Any]) -> Optional[str]:
        #     """
        #     이메일 메시지에서 HTML 본문 추출

        #     Args:
        #         message : 이메일 메시지 객체

        #     Returns:
        #         HTML 본문 또는 None
        #     """
        # parts = [message['payload']]
        
        # while parts:
        #     part = parts.pop(0)
            
        #     if 'parts' in part:
        #         parts.extend(part['parts'])