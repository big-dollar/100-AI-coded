import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from ui.main_window_qt import MainWindowQt
from ui.tray_icon_qt import TrayIconQt
from database.db_manager import DatabaseManager

class TodoAppQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("待办事项提醒 - Author: Big-Dollar")
        self.setGeometry(100, 100, 800, 600)

        # 数据目录
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.db = DatabaseManager(os.path.join(data_dir, "todos.db"))

        # 托盘图标
        self.tray_icon = TrayIconQt(self)
        self.tray_icon.show()

        # 主窗口
        self.main_window = MainWindowQt(self, self.db, self.tray_icon)
        self.setCentralWidget(self.main_window)
        self.tray_icon.set_show_window_callback(self.show_window)

    def show_window(self):
        self.showNormal()
        self.activateWindow()