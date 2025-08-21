import bcrypt
from typing import Final, Optional, List, TypedDict
from json import load as json_load, dump as json_dump
from uuid import uuid4


# ========== Constants ==========
DATA_PATH: Final[str] = "data.json"


# ========== TypedDict ==========
class User(TypedDict):
    name: str
    id: str
    password: str


class Data(TypedDict):
    users: List[User]


# ========== Manager Classes =========
class EnhancedPasswordManager:
    @staticmethod
    def hash_password(password: str, username: str, user_id: str) -> str:
        combined: Final[bytes] = f"{password}:{username}:{user_id}".encode('utf-8')
        hashed: Final[bytes] = bcrypt.hashpw(combined, bcrypt.gensalt())
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, username: str, user_id: str, stored_hash: str) -> bool:
        combined: Final[bytes] = f"{password}:{username}:{user_id}".encode('utf-8')
        return bcrypt.checkpw(combined, stored_hash.encode('utf-8'))
    

class DataManager:
    @staticmethod
    def get_data() -> Data:
        with open(DATA_PATH, 'r', encoding='utf-8') as file:
            return json_load(file)

    @staticmethod
    def get_user_password(user_id: str, user_name: str) -> Optional[str]:
        data: Final[Data] = DataManager.get_data()
        for user in data["users"]:
            if user["id"] == user_id and user["name"] == user_name:
                return user["password"]
        return None

    @staticmethod
    def new_user(user_name: str, user_password: str) -> str:
        data: Final[Data] = DataManager.get_data()

        user_id: Final[str] = str(uuid4()).upper()
        password_encode: Final[str] = EnhancedPasswordManager.hash_password(user_password, user_name, user_id)
        data["users"].append({
            "name": user_name,
            "id": user_id,
            "password": password_encode
        })

        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json_dump(data, f, ensure_ascii=False, indent=4)

        return user_id

    @staticmethod
    def delete_user(user_id: str) -> bool:
        data: Final[Data] = DataManager.get_data()
        flag: bool = False

        for user in data["users"]:
            if user["id"] == user_id:
                flag = True
                data["users"].remove(user)
                break
        
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json_dump(data, f, ensure_ascii=False, indent=4)

        return flag
    
    @staticmethod
    def change_user_info(user_id: str, new_user_name: str, new_user_password: str):
        data: Final[Data] = DataManager.get_data()
        users: Final[List[User]] = data["users"]
        flag: bool = False

        for i in range(len(users)):
            if users[i]["id"] == user_id:
                flag = True
                new_password_encode: str = EnhancedPasswordManager.hash_password(new_user_password, new_user_name, user_id)
                users[i]["name"] = new_user_name
                users[i]["password"] = new_password_encode
                break
        
        data["users"] = users
        
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json_dump(data, f, ensure_ascii=False, indent=4)

        return flag
