import api
from typing import Final, Optional
from threading import Timer
from datetime import datetime
from sys import exit


# ========== Constants =========
CONFIG: Final[api.Config] = api.get_config()
USER_ID: Final[str] = CONFIG["Server"]["USER_ID"]
USER_NAME: Final[str] = CONFIG["Server"]["USER_NAME"]
USER_PASSWORD: Final[str] = CONFIG["Server"]["USER_PASSWORD"]
SERVER_URL: Final[str] = CONFIG["Server"]["SERVER_URL"]
SEND_GAP: Final[int] = CONFIG["Send"]["SEND_GAP"]


def get_active_window_title() -> None:
    global active_window_last

    active_window: Final[Optional[str]] = api.get_active_window_title()

    if not active_window:
        print(f"[info] [Active window] [{datetime.now()}] No active window found.")
        return
    else:
        print(f"[info] [Active window] [{datetime.now()}] {active_window}")
    
    upload_results: Final[dict] = api.upload_info(USER_ID, USER_NAME, USER_PASSWORD, active_window, SERVER_URL)
    if upload_results["status"] == "success":
        print(f"[info] [Upload] [{datetime.now()}] Upload successful.")
    else:
        print(f"[error] [Upload] [{datetime.now()}] Upload failed: {upload_results['message']}")
            
    Timer(SEND_GAP / 1000, start_timer).start()


def start_timer() -> None:
    Timer(SEND_GAP / 1000, get_active_window_title).start()


# Main code
if __name__ == "__main__":
    print("========== Configuration =========")
    print(f"User ID: {USER_ID}")
    print(f"User Name: {USER_NAME}")
    print(f"Server URL: {SERVER_URL}")
    print(f"Send Gap: {SEND_GAP} ms")

    print("========== Login =========")
    login_results: Final[dict] = api.login_web(USER_ID, USER_NAME, USER_PASSWORD, SERVER_URL)
    if login_results["status"] == "success":
        print(f"[info] [Login] [{datetime.now()}] Login successful.")
    else:
        print(f"[error] [Login] [{datetime.now()}] Login failed: {login_results['message']}")
        input("Press Enter to exit.")
        exit(1)

    print("========== Logs =========")
    start_timer()
