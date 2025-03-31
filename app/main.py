"""
구글 알리미 이메일을 가져와 로컬에 MCP가 사용할 수 있게 저장하는 프로그램
"""
import logging
# import schedule
# import time
from app.gmail_client import GoogleAlertClient

import sys
import os

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """메인 함수"""
    logger.info("Google Alert API 시작")
    # Gamil 클라이언트와 저장소 초기화
    gmail_client = GoogleAlertClient()
    
    # 저장소 초기화
    # storage = AlertStorage()
    
    # 알림 처리 함수
    def process_alerts():
        try:
            logger.info("구글 알리미 이메일 확인 중...")
            alerts = gmail_client.fetch_google_alerts()
            if alerts : 
                logger.info(f"{len(alerts)}개의 알림을 찾았습니다.")
                for alert in alerts:
                    print(alert)
            return True
                
        except Exception as e:
            logger.error(f"알림 처리 중 오류 발생: {e}")
            return False
        
    # 초기 실행
    success = process_alerts()
    if not success:
        logger.warning("실행 실패")
if __name__ == "__main__":
    main()
