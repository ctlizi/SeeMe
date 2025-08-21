import sys
from typing import Final, List, Union
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QStackedWidget, QListWidget,
                             QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import api


class AddUserWidget(QWidget):
    def __init__(self, parent: Union[QWidget, None] = None) -> None:
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self) -> None:
        layout: Final[QVBoxLayout] = QVBoxLayout(self)
        
        title: Final[QLabel] = QLabel("ADD USER")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        
        self.username_input: QLineEdit = QLineEdit()
        self.username_input.setPlaceholderText("User name")
        
        self.password_input: QLineEdit = QLineEdit()
        self.password_input.setPlaceholderText("User password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        add_button: Final[QPushButton] = QPushButton("Add User")
        add_button.clicked.connect(self.add_user)
        
        layout.addWidget(title)
        layout.addWidget(QLabel("User Name:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(add_button)
        layout.addStretch()
        
    def add_user(self) -> None:
        username: Final[str] = self.username_input.text().strip()
        password: Final[str] = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Empty user name or user password.")
            return
            
        try:
            user_id: Final[str] = api.DataManager.new_user(username, password)
            QMessageBox.information(self, "Success", f"Add success! New user ID: {user_id}")
            self.username_input.clear()
            self.password_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")


class DeleteUserWidget(QWidget):
    def __init__(self, parent: Union[QWidget, None] = None) -> None:
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self) -> None:
        layout: Final[QVBoxLayout] = QVBoxLayout(self)
        
        title: Final[QLabel] = QLabel("DELETE USER")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        
        self.user_id_input: QLineEdit = QLineEdit()
        self.user_id_input.setPlaceholderText("User ID")
        
        delete_button: Final[QPushButton] = QPushButton("Delete User")
        delete_button.clicked.connect(self.delete_user)
        
        layout.addWidget(title)
        layout.addWidget(QLabel("User ID:"))
        layout.addWidget(self.user_id_input)
        layout.addWidget(delete_button)
        layout.addStretch()
        
    def delete_user(self) -> None:
        user_id: Final[str] = self.user_id_input.text().strip()
        
        if not user_id:
            QMessageBox.warning(self, "Error", "Please enter a user ID.")
            return
            
        try:
            delete_flag: Final[bool] = api.DataManager.delete_user(user_id)
            if delete_flag:
                QMessageBox.information(self, "Success", "Delete success!")
                self.user_id_input.clear()
            else:
                QMessageBox.warning(self, "Error", "User not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")


class ChangeUserInfoWidget(QWidget):
    def __init__(self, parent: Union[QWidget, None] = None) -> None:
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self) -> None:
        layout: Final[QVBoxLayout] = QVBoxLayout(self)
        
        title: Final[QLabel] = QLabel("CHANGE USER INFO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        
        self.user_id_input: QLineEdit = QLineEdit()
        self.user_id_input.setPlaceholderText("User ID")
        
        self.new_username_input: QLineEdit = QLineEdit()
        self.new_username_input.setPlaceholderText("New user name")
        
        self.new_password_input: QLineEdit = QLineEdit()
        self.new_password_input.setPlaceholderText("New user password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        
        change_button: Final[QPushButton] = QPushButton("Change User Info")
        change_button.clicked.connect(self.change_user_info)
        
        layout.addWidget(title)
        layout.addWidget(QLabel("User ID:"))
        layout.addWidget(self.user_id_input)
        layout.addWidget(QLabel("New User Name:"))
        layout.addWidget(self.new_username_input)
        layout.addWidget(QLabel("New Password:"))
        layout.addWidget(self.new_password_input)
        layout.addWidget(change_button)
        layout.addStretch()
        
    def change_user_info(self) -> None:
        user_id: Final[str] = self.user_id_input.text().strip()
        new_username: Final[str] = self.new_username_input.text().strip()
        new_password: Final[str] = self.new_password_input.text().strip()
        
        if not new_username or not new_password:
            QMessageBox.warning(self, "Error", "Empty user name or user password.")
            return
            
        try:
            change_flag: Final[bool] = api.DataManager.change_user_info(user_id, new_username, new_password)
            if change_flag:
                QMessageBox.information(self, "Success", "Change user info success!")
                self.user_id_input.clear()
                self.new_username_input.clear()
                self.new_password_input.clear()
            else:
                QMessageBox.warning(self, "Error", "User not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to change user info: {str(e)}")


class AllUsersWidget(QWidget):
    def __init__(self, parent: Union[QWidget, None] = None) -> None:
        super().__init__(parent)
        self.setup_ui()
        self.load_users()
        
    def setup_ui(self) -> None:
        layout: Final[QVBoxLayout] = QVBoxLayout(self)
        
        title: Final[QLabel] = QLabel("ALL USERS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        
        buttons_layout: Final[QHBoxLayout] = QHBoxLayout(self)

        refresh_button: Final[QPushButton] = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_users)

        copy_id_button: Final[QPushButton] = QPushButton("Copy ID")
        copy_id_button.clicked.connect(self.copy_id);
        
        self.users_list: QListWidget = QListWidget()
        
        layout.addWidget(title)
        buttons_layout.addWidget(refresh_button)
        buttons_layout.addWidget(copy_id_button)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.users_list)
    
    def copy_id(self) -> None:
        selections: List[QListWidgetItem] = self.users_list.selectedItems()

        if len(selections) <= 0:
            QMessageBox().critical(self, "Error", "No selections found.")
            return

        select_id: Final[str] = selections[0].text().split("\n")[1].split(":")[1].strip()
        
        clipboard = QApplication.clipboard()
        clipboard.setText(select_id)

        QMessageBox().information(self, "Sucess", "Copy sucess.")


    def load_users(self) -> None:
        self.users_list.clear()
        try:
            users_data: api.Data = api.DataManager.get_data()
            users: List[api.User] = users_data.get("users", [])
            
            if not users:
                item: QListWidgetItem = QListWidgetItem("No users found")
                item.setTextAlignment(Qt.AlignCenter)
                self.users_list.addItem(item)
                return
                
            for user in users:
                item_text: str = f"User name: {user['name']}\nUser ID: {user['id']}"
                item: QListWidgetItem = QListWidgetItem(item_text)
                self.users_list.addItem(item)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SEEME ADMIN")
        self.setMinimumSize(600, 500)
        self.setup_ui()
        
    def setup_ui(self) -> None:
        central_widget: Final[QWidget] = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout: Final[QHBoxLayout] = QHBoxLayout(central_widget)
        
        # Sidebar with navigation buttons
        sidebar: Final[QWidget] = QWidget()
        sidebar.setFixedWidth(150)
        sidebar_layout: Final[QVBoxLayout] = QVBoxLayout(sidebar)
        
        self.add_user_btn: QPushButton = QPushButton("Add User")
        self.delete_user_btn: QPushButton = QPushButton("Delete User")
        self.change_info_btn: QPushButton = QPushButton("Change Info")
        self.all_users_btn: QPushButton = QPushButton("All Users")
        self.exit_btn: QPushButton = QPushButton("Exit")
        
        sidebar_layout.addWidget(self.add_user_btn)
        sidebar_layout.addWidget(self.delete_user_btn)
        sidebar_layout.addWidget(self.change_info_btn)
        sidebar_layout.addWidget(self.all_users_btn)
        sidebar_layout.addWidget(self.exit_btn)
        sidebar_layout.addStretch()
        
        # Stacked widget for different views
        self.stacked_widget: QStackedWidget = QStackedWidget()
        
        self.add_user_widget: AddUserWidget = AddUserWidget()
        self.delete_user_widget: DeleteUserWidget = DeleteUserWidget()
        self.change_info_widget: ChangeUserInfoWidget = ChangeUserInfoWidget()
        self.all_users_widget: AllUsersWidget = AllUsersWidget()
        
        self.stacked_widget.addWidget(self.add_user_widget)
        self.stacked_widget.addWidget(self.delete_user_widget)
        self.stacked_widget.addWidget(self.change_info_widget)
        self.stacked_widget.addWidget(self.all_users_widget)
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)
        
        # Connect signals
        self.add_user_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.delete_user_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.change_info_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.all_users_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.exit_btn.clicked.connect(self.close)
        
        # Set initial view
        self.stacked_widget.setCurrentIndex(0)


def main() -> None:
    app: Final[QApplication] = QApplication(sys.argv)

    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window: Final[MainWindow] = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
