"""
구글 알리미 이메일을 가져와 로컬에 MCP가 사용할 수 있게 저장하는 프로그램
"""
import logging
import schedule
import time
from app.gmail_client import GoogleAlertClient

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
    # def process_alerts():
    #     try:
    #         logger.info("구글 알리미 이메일 확인 중...")
    #         a        
        
if __name__ == "__main__":
    main()
