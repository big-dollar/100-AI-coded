from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication, QDialog
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt
import os
import sys
from .todo_dialog import TodoDialog

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class TrayIconQt(QSystemTrayIcon):
    def __init__(self, parent):
        icon_path = get_resource_path("ui/todo.ico")
        super().__init__(QIcon(icon_path), parent)
        self.parent = parent
        self.show_window_callback = None
        self.init_ui()
        self.activated.connect(self.on_tray_activated)

    def init_ui(self):
        """初始化托盘图标UI"""
        self.menu = QMenu()
        
        # 创建菜单项
        self.add_action = QAction("新增待办", self)
        self.show_action = QAction("显示主窗口", self)
        self.exit_action = QAction("退出", self)
        
        # 连接信号
        self.add_action.triggered.connect(self.on_add_todo)
        self.show_action.triggered.connect(self.on_show_window)
        self.exit_action.triggered.connect(self.on_exit)
        
        # 添加菜单项
        self.menu.addAction(self.add_action)
        self.menu.addAction(self.show_action)
        self.menu.addAction(self.exit_action)
        
        self.setContextMenu(self.menu)

    def on_add_todo(self):
        """处理添加待办事项"""
        dialog = TodoDialog()
        if dialog.exec_() == QDialog.Accepted:
            title, desc, due = dialog.get_data()
            if title.strip():
                self.parent.db.add_todo(title, desc, due)
                if hasattr(self.parent.main_window, 'load_todos'):
                    self.parent.main_window.load_todos()
                self.showMessage("待办事项提醒", "已成功添加新待办事项")

    def on_tray_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.on_show_window()

    def update_icon_with_count(self, count):
        """更新托盘图标显示待办数量"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        
        # 绘制基础图标
        icon_path = get_resource_path("ui/todo.ico")
        icon = QIcon(icon_path)
        icon_pix = icon.pixmap(64, 64)
        painter.drawPixmap(0, 0, icon_pix)
        
        # 如果有待办事项，显示数量
        if count > 0:
            painter.setPen(QColor("red"))
            painter.setFont(QFont("Arial", 28, QFont.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignBottom | Qt.AlignRight, str(count))
        
        painter.end()
        self.setIcon(QIcon(pixmap))

    def set_show_window_callback(self, callback):
        """设置显示窗口的回调函数"""
        self.show_window_callback = callback

    def on_show_window(self):
        """显示主窗口"""
        if self.show_window_callback:
            self.show_window_callback()

    def on_exit(self):
        """退出应用程序"""
        self.parent.close()
        QApplication.instance().quit()