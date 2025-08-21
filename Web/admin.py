import api
from typing import Final, List
from sys import exit


def add_new_user():
    print("========== ADD USER =========")
    user_name: Final[str] = input("User name: ")
    user_password: Final[str] = input("User password: ")

    if (user_name == "" or user_password == ""):
        print(f"[Error] Empty user name or user password.")
        return

    user_id: Final[str] = api.DataManager.new_user(user_name, user_password)
    print(f"[Sucess] Add sucess! new user ID: {user_id}")


def delete_user():
    print("========== DELETE USER =========")
    user_id: Final[str] = input("User ID: ")
    delete_flag: Final[bool] = api.DataManager.delete_user(user_id)

    if delete_flag:
        print("[Sucess] Delete sucess!")
    else:
        print("[Error] User not found.")


def change_user_info():
    print("========== CHANGE USER INFO =========")
    user_id: Final[str] = input("User ID: ")
    new_user_name: Final[str] = input("New user name: ")
    new_user_password: Final[str] = input("New user password: ")

    if (new_user_name == "" or new_user_password == ""):
        print(f"[Error] Empty user name or user password.")
        return

    change_flag: Final[bool] = api.DataManager.change_user_info(user_id, new_user_name, new_user_password)
    if change_flag:
        print("[Sucess] Change user info sucess!")
    else:
        print("[Error] User not found.")


def get_all_users():
    print("========== ALL USERS =========")
    users: List[api.User] = api.DataManager.get_data()["users"];
    for i in range(len(users)):
        print(f"User name: {users[i]['name']}")
        print(f"User ID: {users[i]['id']}")
        if i < len(users) - 1:
            print("====================")


def main():
    print("========== SEEME ADMIN =========")
    print("[1] Add new user")
    print("[2] Delete user")
    print("[3] Change user info")
    print("[4] Get all users")
    print("[5] Exit")

    choice: Final[int] = int(input("Enter your choice: "))
    if choice == 1: add_new_user()
    elif choice == 2: delete_user()
    elif choice == 3: change_user_info()
    elif choice == 4: get_all_users()
    elif choice == 5: exit(0)
    else: print("[Error] Operate not found, please enter else choice.")


if __name__ == "__main__":
    while True: main()
