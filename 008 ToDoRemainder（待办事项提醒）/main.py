import sys
from PyQt5.QtWidgets import QApplication
from todo_app_qt import TodoAppQt

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 添加这行
    window = TodoAppQt()
    window.show()
    sys.exit(app.exec_())