import imaplib
import os
import logging
import base64
from datetime import datetime
from typing import List,Dict,Any,Optional
from bs4 import BeautifulSoup
import urllib.parse


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES, ALERTS_QUERY


import traceback

logger = logging.getLogger(__name__)
class GoogleAlertClient:
    def __init__(self):
        self._service = self.get_gmail_service()

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
            results = self._service.users().messages().list(
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
    def _process_message(self, msg_id: str) -> Optional[Dict[str, Any]]:
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
            body = self._get_message_body(message)
            if not body:
                logger.warning(f"메시지 {msg_id}에서 본문을 추출할 수 없습니다.")
                return None

            alert_items = self._parse_alert_html(body)
            # print(alert_items)
            return {
                'id':msg_id,
                'items':alert_items
            }
            
        except Exception as e:
            logger.error(f"메시지 {msg_id} 처리 중 오류 발생: {e}")
            return None
        
    def _get_message_body(self, message: Dict[str, Any]) -> Optional[str]:
        """
        이메일 메시지에서 HTML 본문 추출

        Args:
            message : 이메일 메시지 객체

        Returns:
            HTML 본문 또는 None
        """
        parts = [message['payload']]
        
        while parts:
            part = parts.pop(0)
            
            if 'parts' in part:
                parts.extend(part['parts'])
            
            if 'body' in part and 'data' in part['body']:
                mime_type = part.get('mimeType')
                if mime_type =='text/html':
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        return None

    def _parse_alert_html(self, html: str) -> List[Dict[str,str]]:
        """
        알림 HTML을 파싱하여 항목을 추출합니다.

        Args:
            html (str): HTML 문자열

        Returns:
            추출된 알림 항목목록
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            valid_links = []
            tables = soup.find_all('table', style="border-collapse:collapse;border-left:1px solid #e4e4e4;border-right:1px solid #e4e4e4")
            # print(tables)
            for table in tables:
                links = []
                # <tr> 태그 순회
                for idx, tr in enumerate(table.find_all('tr')):
                    
                    tds = tr.select('td[style*="font-family:Arial"]') # css 선택자 이용, 첫 번째 링크랑 다른링크들이랑 차이 약간 있어서 전부 때려넣으면 오류

                    for td in tds:
                    # <a> 태그 찾기
                        a_tags = td.find_all('a', href=True) # 그냥 a만 찾으면 빈 a 있어서 그거 반환함
                        for a_tag in a_tags:
                            # <a> 태그 안에 이미지가 있는지 확인
                            img_tag = td.find('img')
                            if img_tag:
                                # 이미지와 텍스트가 같은 링크를 제외
                                if img_tag['src'] in a_tag.get_text():
                                    continue  # 이미지와 텍스트가 같으면 제외

                            links.append(a_tag['href'])
                            
                #TODO 반환 구조를 설정한 알리미 태그도 함께 넘겨줘야 정리할 때 유용할 것같음
                for idx,link in enumerate(links):

                    parsed_link = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)

                    real_link = parsed_link.get('url', [None])[0]
                    
                    if real_link is None : 
                        continue
                    valid_links.append(real_link)
                    
        except Exception as e:
            error_message = traceback.format_exc()
            logger.error(f"fetch 처리 중 오류 발생: {error_message}")
        return valid_links