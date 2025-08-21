import ctypes
from ctypes import wintypes
from typing import Optional, TypedDict, Final
from configparser import ConfigParser
from requests import post


# ========== Constants =========
CONFIG_PATH: Final[str] = "config.ini"
SERVER_SECTION: Final[str] = "Server"
SEND_SECTION: Final[str] = "Send"
SERVER_URL_KEY: Final[str] = "SERVER_URL"
USER_ID_KEY: Final[str] = "USER_ID"
USER_NAME_KEY: Final[str] = "USER_NAME"
USER_PASSWORD_KEY: Final[str] = "USER_PASSWORD"
SEND_GAP_KEY: Final[str] = "SEND_GAP"


# ========== TypedDicts =========
class Server(TypedDict):
    SERVER_URL: str
    USER_ID: str
    USER_NAME: str
    USER_PASSWORD: str


class Send(TypedDict):
    SEND_GAP: int


class Config(TypedDict):
    Server: Server
    Send: Send


class UploadInfo(TypedDict):
    user_id: str
    user_name: str
    user_password: str
    active_window: Optional[str]


class LoginInfo(TypedDict):
    user_id: str
    user_name: str
    user_password: str


# ========== Functions =========
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD)
    ]


def get_config() -> Config:
    parser: Final[ConfigParser] = ConfigParser()
    parser.read(CONFIG_PATH, encoding="utf-8")
    return {
        "Server": {
            "SERVER_URL": parser.get(SERVER_SECTION, SERVER_URL_KEY),
            "USER_ID": parser.get(SERVER_SECTION, USER_ID_KEY),
            "USER_NAME": parser.get(SERVER_SECTION, USER_NAME_KEY),
            "USER_PASSWORD": parser.get(SERVER_SECTION, USER_PASSWORD_KEY)
        },
        "Send": {
            "SEND_GAP": int(parser.get(SEND_SECTION, SEND_GAP_KEY))
        }
    }

def get_idle_time() -> float:
    
    last_input_info: LASTINPUTINFO = LASTINPUTINFO()
    last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    
    user32: ctypes.WinDLL = ctypes.WinDLL('user32', use_last_error=True)
    kernel32: ctypes.WinDLL = ctypes.WinDLL('kernel32', use_last_error=True)
    
    if user32.GetLastInputInfo(ctypes.byref(last_input_info)):
        current_time: int = kernel32.GetTickCount()
        idle_time_ms: int = current_time - last_input_info.dwTime
        return idle_time_ms / 1000.0
    return 0.0


def get_active_window_title() -> Optional[str]:
    if get_idle_time() > 10: return None

    try:
        user32: ctypes.WinDLL = ctypes.WinDLL('user32', use_last_error=True)
        h_wnd: int = user32.GetForegroundWindow()
        
        if not h_wnd:
            return None
            
        length: int = user32.GetWindowTextLengthW(h_wnd)
        if length <= 0:
            return None
            
        buffer: ctypes.Array[ctypes.c_wchar] = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(h_wnd, buffer, length + 1)
        return buffer.value if buffer.value else None
        
    except Exception:
        return None


def login_web(user_id: str, user_name: str, user_password: str, server_url: str) -> dict:
    login_info: Final[LoginInfo] = {
        "user_id": user_id,
        "user_name": user_name,
        "user_password": user_password
    }

    headers: Final[dict] = {
        "Content-Type": "application/json"
    }

    response = post(f"{server_url}/login", json=login_info, headers=headers)
    return response.json()


def upload_info(user_id: str, user_name: str, user_password: str, active_window: str, server_url: str) -> dict:
    upload_info: Final[UploadInfo] = {
        "user_id": user_id,
        "user_name": user_name,
        "user_password": user_password,
        "active_window": active_window
    }

    headers: Final[dict] = {
        "Content-Type": "application/json"
    }

    response = post(f"{server_url}/upload", json=upload_info, headers=headers)
    return response.json()


# ========== Test Code =========
if __name__ == "__main__":
    activeWindow: Final[Optional[str]] = get_active_window_title()
    print(activeWindow)
    print(get_config())
