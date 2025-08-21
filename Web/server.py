import flask
from typing import Final, TypedDict, Optional, List
from api import DataManager, EnhancedPasswordManager, Data
from time import time


# ========== TypedDicts =========
class UploadInfo(TypedDict):
    user_id: str
    user_name: str
    user_password: str
    active_window: str


class LoginInfo(TypedDict):
    user_id: str
    user_name: str
    user_password: str


class User(TypedDict):
    user_id: str
    active_window: str
    update_time: float


class UserListData(TypedDict):
    user_id: str
    user_name: str


class UserActiveWindow(TypedDict):
    active_window: str
    update_time: float


# ========== Golbal Viants =========
login_dict: List[LoginInfo] = []
users: List[User] = []

# ========== Inits =========
def init_users() -> None:
    data: Final[Data] = DataManager.get_data()
    for user in data.get("users", []):
        users.append({
            "user_id": user["id"],
            "active_window": "Unknow",
            "update_time": time() - 60
        })
    print(f"[info] [Init] Loaded {len(users)} users from data.json.")


# ========== Server =========
port: Final[int] = 5050
static_folder: Final[str] = ""
app: Final[flask.Flask] = flask.Flask(__name__, static_folder=static_folder)


@app.route("/", methods=["GET"])
def home() -> flask.Response:
    return flask.send_file("public/index.html")


@app.route("/login", methods=["POST"])
def login() -> flask.Response:
    data: Final[Optional[LoginInfo]] = flask.request.json

    if not data:
        return flask.jsonify({"error": "Invalid data"})

    user_id: Final[str] = data["user_id"]
    user_name: Final[str] = data["user_name"]
    user_password: Final[str] = data["user_password"]

    stored_password: Final[Optional[str]] = DataManager.get_user_password(user_id, user_name)
    print(f"[info] [Login] [{user_id}] Attempting login with user name: {user_name}")
    print(f"[info] [Login] [{user_id}] Stored password: {stored_password}")
    if not stored_password:
        return flask.jsonify({"status": "error", "message": "User or password error"})
    
    if EnhancedPasswordManager.verify_password(user_password, user_name, user_id, stored_password):
        if not data in login_dict:
            login_dict.append(data)
        return flask.jsonify({"status": "success", "message": "Login successful"})
    else:
        return flask.jsonify({"status": "error", "message": "User or password error"})


@app.route("/upload", methods=["POST"])
def upload() -> flask.Response:
    data: Final[Optional[UploadInfo]] = flask.request.json

    if not data:
        return flask.jsonify({"status": "error", "message": "Invalid data"})

    user_id: Final[str] = data["user_id"]
    user_name: Final[str] = data["user_name"]
    user_password: Final[str] = data["user_password"]
    active_window: Final[str] = data["active_window"]

    login_info: LoginInfo = {
        "user_id": user_id,
        "user_name": user_name,
        "user_password": user_password
    }

    if login_info not in login_dict:
        return flask.jsonify({"status": "error", "message": "User not logged in"})

    user_data: Final[User] = {
                "user_id": user_id,
                "active_window": active_window,
                "update_time": time()
            }
    
    for i in range(len(users)):
        if users[i]["user_id"] == user_id:
            users[i] = user_data
            break

    return flask.jsonify({"status": "success", "message": "Upload successful"})


@app.route("/users", methods=["GET"])
def get_users_list() -> flask.Response:
    user_list: List[UserListData] = []
    for user in DataManager.get_data().get("users", []):
        user_list.append({
            "user_id": user["id"],
            "user_name": user["name"]
        })
    return flask.jsonify({"status": "success", "data": user_list})


@app.route("/users/get", methods=["POST"])
def get_user_info() -> flask.Response:
    data: Final[Optional[dict]] = flask.request.json

    if not data:
        return flask.jsonify({"status": "error", "message": "Invalid data"})

    user_id: Final[Optional[str]] = data.get("user_id", None)

    if not user_id:
        return flask.jsonify({"status": "error", "message": "Invalid data"})

    for user in users:
        if user["user_id"] == user_id:
            active_window: UserActiveWindow = {
                "active_window": user["active_window"],
                "update_time": user["update_time"]
            }
            return flask.jsonify({"status": "success", "data": active_window})

    return flask.jsonify({"status": "error", "message": "Data not found."})


# ========== Main =========
if __name__ == "__main__":
    init_users()
    print(f"[info] [Server] Starting server on port {port}...")
    app.run(port=port, debug=True)
