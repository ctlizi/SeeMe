from pygetwindow import getActiveWindowTitle
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


def get_active_window_title() -> Optional[str]:
    return getActiveWindowTitle()


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
