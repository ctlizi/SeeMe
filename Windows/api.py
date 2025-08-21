import ctypes
from ctypes import wintypes
from typing import Optional, TypedDict, Final
from configparser import ConfigParser
from requests import post


# ========== TypedDicts =========
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
    try:
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
    except Exception as e:
        return {"status": "error", "message": f"Connect Error: {str(e)}"}


def upload_info(user_id: str, user_name: str, user_password: str, active_window: str, server_url: str) -> dict:
    try:
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
    except Exception as e:
        return {"status": "error", "message": f"Connect Error: {str(e)}"}


# ========== Test Code =========
if __name__ == "__main__":
    activeWindow: Final[Optional[str]] = get_active_window_title()
    print(activeWindow)
