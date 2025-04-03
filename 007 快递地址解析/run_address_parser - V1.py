import os
import sys
import subprocess

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 检查并安装必要的包
required_packages = ["pandas", "openpyxl", "cpca"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"正在安装 {package}...")
        install_package(package)

# 运行主程序
if __name__ == "__main__":
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "address_parser_gui.py")
    subprocess.call([sys.executable, script_path])