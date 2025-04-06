from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from app.google_alert_client import GoogleAlertClient

# FastMCP서버 초기화
mcp = FastMCP(
    "myalert_mcp_server",
    dependencies=[
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "beautifulsoup4",
    ],
)

@mcp.tool(
    name="get_alert_links",
    descripton="Fetch and return Google Alert links from Gmail"
)
def get_alert_links(max_results: int = 3):
    """
    Gmail에서 구글 알리미 메일을 가져와 링크를 추출

    Args:
        max_results (int): 가져올 최대 알림 수
    """
    client = GoogleAlertClient()
    alerts = client.fetch_google_alerts(max_results=max_results)
    return alerts