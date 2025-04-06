import subprocess
import pyautogui
import pygetwindow as gw
import time
import psutil
import os
import json
import logging

logger = logging.getLogger(__name__)

CACHE_FILE = os.path.join(".cache", "ui_location_cache.json")
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
img_name = "input.png"
#TODO 클로드 위치 찾는 로직, 창 최대화 시키는 로직, 최적화 필요, 클릭로직 필요없을듯...
def is_claude_running():
    """
    클로드 실행 확인하는 로직

    Returns:
        _type_: bool
    """
    for proc in psutil.process_iter(['name']):
        if 'claude' in proc.info['name'].lower():
            return True
    return False

def launch_claude():
    """
    클로드 실행 시키는 함수
    """
    subprocess.Popen([r"C:\Users\PC\AppData\Local\AnthropicClaude\Claude.exe"])
    time.sleep(5)
    
def save_location_cache(img_name:str,x,y):
    
    cache = {}
    cache[img_name] = [x, y]
    
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def load_location_cache(img_name: str):
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            return cache.get(img_name)
    return {}

def send_first_prompt(prompt_text, app_title="Claude"):
    windows = [w for w in gw.getWindowsWithTitle(app_title) if w.visible]
    if not windows:
        launch_claude()
    win = windows[0]
    
    win.activate()
    time.sleep(0.5)
    
    if not win.isMaximized:
        win.maximize()
        pyautogui.hotkey("alt", "space")
        pyautogui.press("x")
    
    cached_location = load_location_cache(img_name)
    try:
        if cached_location:
            x,y = cached_location     
        else:
            img_path = os.path.join(os.path.dirname(__file__), "..", "images", img_name)
            if img_path:
                print(img_path)
            location = pyautogui.locateOnScreen(img_path)
            if location: 
                x,y = pyautogui.center(location)
                save_location_cache(img_name,x,y)
                
        pyautogui.click(x,y)
        time.sleep(0.2)

        pyautogui.typewrite(prompt_text, interval=0.05)
        pyautogui.press('enter')
    except Exception as e:
        logger.error(f"자동화 처리 중 오류 발생: {e}")
        return None
    
if __name__ == "__main__":
    prompt = "오늘의 날씨는?"
    if not is_claude_running():
        launch_claude()
    send_first_prompt(prompt)