import sys
import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, QScrollArea, 
                            QGridLayout, QLabel, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QIcon
from PyQt5.QtCore import Qt, QByteArray, QBuffer, QSize, QRect, QRectF
from PyQt5.QtSvg import QSvgRenderer
import logging
import datetime
import glob
import shutil

# 设置日志
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 清理历史日志和JSON文件
def clean_log_directory(log_dir):
    try:
        # 删除所有日志文件
        for log_file in glob.glob(os.path.join(log_dir, '*.log')):
            os.remove(log_file)
        
        # 删除所有JSON文件
        for json_file in glob.glob(os.path.join(log_dir, '*.json')):
            os.remove(json_file)
            
        logging.info(f"已清理历史日志和JSON文件")
    except Exception as e:
        logging.error(f"清理日志目录时出错: {str(e)}")

# 清理历史文件
clean_log_directory(log_dir)

# 创建新的日志文件
log_file = os.path.join(log_dir, f'icon_search_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 记录应用启动信息
logging.info("应用启动")
logging.info(f"日志文件: {log_file}")

# 定义应用样式
STYLE_SHEET = """
QWidget {
    font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
    font-size: 16px;  /* 进一步增大基础字体大小 */
    color: #333333;
    background-color: #f5f5f5;
}

QMainWindow {
    background-color: #f5f5f5;
}

QLineEdit {
    padding: 8px 12px;
    border: 1px solid #e0e0e0;
    border-radius: 20px;
    background-color: white;
    selection-background-color: #0078d7;
    font-size: 16px;  /* 增大搜索框字体 */
}

QLineEdit:focus {
    border: 1px solid #0078d7;
}

QPushButton {
    padding: 8px 20px;  /* 增加水平内边距 */
    border: none;
    border-radius: 20px;
    background-color: #0078d7;
    color: white;  /* 确保按钮文字为白色 */
    font-weight: bold;
    font-size: 16px;  /* 增大按钮字体 */
}

QPushButton:hover {
    background-color: #0086f0;
}

QPushButton:pressed {
    background-color: #006ac1;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #888888;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QLabel {
    color: #333333;
    font-size: 16px;  /* 增大标签字体 */
}

QGridLayout {
    margin: 10px;
}
"""

class SvgIconWidget(QWidget):
    def __init__(self, svg_content, icon_name, parent=None):
        super().__init__(parent)
        self.svg_content = svg_content
        self.icon_name = icon_name
        self.setFixedSize(130, 150)  # 增大图标小部件尺寸
        self.setCursor(Qt.PointingHandCursor)
        self.hovered = False
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        bg_color = QColor(255, 255, 255) if not self.hovered else QColor(240, 248, 255)
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(self.rect(), 10, 10)
        
        # 绘制边框
        if self.hovered:
            painter.setPen(QColor(0, 120, 215))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 10, 10)
        
        # 绘制SVG图标
        renderer = QSvgRenderer(QByteArray(self.svg_content.encode()))
        icon_size = 90  # 增大图标尺寸
        x = (self.width() - icon_size) // 2
        y = 15
        renderer.render(painter, QRectF(x, y, icon_size, icon_size))
        
        # 绘制图标名称
        painter.setPen(QColor(51, 51, 51))
        font = painter.font()
        font.setPointSize(10)  # 增大图标名称字体
        painter.setFont(font)
        text_rect = QRect(10, 110, self.width()-20, 35)
        painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, self.icon_name)
        
    def enterEvent(self, event):
        self.hovered = True
        self.update()
        
    def leaveEvent(self, event):
        self.hovered = False
        self.update()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.download_svg()
            
    def download_svg(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "保存SVG文件", f"{self.icon_name}.svg", "SVG Files (*.svg)")
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.svg_content)
                QMessageBox.information(self, "下载成功", f"SVG图标已保存到: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "下载失败", f"保存文件时出错: {str(e)}")

class IconDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_page = 1
        self.current_query = ""
        
    def initUI(self):
        self.setWindowTitle('如席矢量图标下载工具')
        self.setGeometry(100, 100, 1200, 800)  # 增大窗口默认尺寸
        
        # 设置应用样式
        self.setStyleSheet(STYLE_SHEET)
        
        # 主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel('如席矢量图标下载工具')
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont('Microsoft YaHei', 22, QFont.Bold)  # 增大标题字体
        title_label.setFont(title_font)
        title_label.setStyleSheet('color: #0078d7; margin-bottom: 10px;')
        main_layout.addWidget(title_label)
        
        # 搜索区域
        search_widget = QWidget()
        search_widget.setStyleSheet('background-color: white; border-radius: 25px; padding: 10px;')
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(15, 5, 15, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入关键词搜索图标...')
        self.search_input.setMinimumHeight(45)  # 增加搜索框高度
        self.search_input.returnPressed.connect(self.search_icons)
        
        self.search_button = QPushButton('搜索')
        self.search_button.setMinimumHeight(45)  # 增加按钮高度
        self.search_button.setMinimumWidth(150)  # 进一步增加按钮宽度，确保文字显示
        self.search_button.setStyleSheet('color: black;')  # 明确设置按钮文字颜色为白色
        self.search_button.clicked.connect(self.search_icons)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        main_layout.addWidget(search_widget)
        
        # 图标显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet('background-color: white; border-radius: 10px;')
        
        self.icons_container = QWidget()
        self.icons_layout = QGridLayout(self.icons_container)
        self.icons_layout.setSpacing(15)
        self.icons_layout.setContentsMargins(20, 20, 20, 20)
        
        self.scroll_area.setWidget(self.icons_container)
        main_layout.addWidget(self.scroll_area)
        
        # 分页控制
        pagination_widget = QWidget()
        pagination_widget.setStyleSheet('background-color: white; border-radius: 20px; padding: 5px;')
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setContentsMargins(10, 5, 10, 5)
        
        self.prev_button = QPushButton('上一页')
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)
        self.prev_button.setStyleSheet('color: black; font-size: 18px; font-weight: bold;')  # 设置文字颜色为黑色并增大字号
        
        self.page_label = QLabel('第1页')
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        
        self.next_button = QPushButton('下一页')
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        self.next_button.setStyleSheet('color: black; font-size: 18px; font-weight: bold;')  # 设置文字颜色为黑色并增大字号
        
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addStretch(1)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addStretch(1)
        pagination_layout.addWidget(self.next_button)
        
        main_layout.addWidget(pagination_widget)
        
        # 底部信息
        footer_label = QLabel('© 2025 如席矢量图标下载工具 - 数据来源于iconfont.cn')
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet('color: #888888; font-size: 14px; margin-top: 5px;')  # 增大页脚字体
        main_layout.addWidget(footer_label)
        
        self.setCentralWidget(main_widget)
        
    def search_icons(self):
        self.current_query = self.search_input.text().strip()
        if not self.current_query:
            QMessageBox.warning(self, "搜索错误", "请输入搜索关键词")
            return
            
        self.current_page = 1
        self.fetch_icons()
        
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.fetch_icons()
            
    def next_page(self):
        self.current_page += 1
        self.fetch_icons()
        
    def fetch_icons(self):
        # 清空当前图标
        self.clear_icons()
        
        # 更新页码显示
        self.page_label.setText(f'第{self.current_page}页')
        
        # 构建API URL
        api_url = "https://www.iconfont.cn/api/icon/search.json"
        logging.info(f"API URL: {api_url}")
        
        try:
            # 显示加载中
            loading_label = QLabel("正在加载图标...")
            loading_label.setAlignment(Qt.AlignCenter)
            self.icons_layout.addWidget(loading_label, 0, 0)
            QApplication.processEvents()
            
            # 首先获取CSRF令牌和Cookie
            session = requests.Session()
            home_url = "https://www.iconfont.cn/search/index"
            home_response = session.get(
                home_url, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
                }
            )
            
            # 从响应中提取CSRF令牌和ctoken
            csrf_token = None
            ctoken = None
            soup = BeautifulSoup(home_response.text, 'html.parser')
            
            # 提取csrf-token
            meta_csrf = soup.find('meta', attrs={'name': 'csrf-token'})
            if meta_csrf:
                csrf_token = meta_csrf.get('content')
                logging.info(f"获取到CSRF令牌: {csrf_token}")
            else:
                logging.warning("未能从页面获取CSRF令牌")
            
            # 提取ctoken (从cookie中)
            for cookie in session.cookies:
                if cookie.name == 'ctoken':
                    ctoken = cookie.value
                    logging.info(f"获取到ctoken: {ctoken}")
                    break
            
            if not ctoken:
                logging.warning("未能从cookie获取ctoken")
            
            # 构建请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://www.iconfont.cn',
                'Referer': f'https://www.iconfont.cn/search/index?searchType=icon&q={urllib.parse.quote(self.current_query)}&page={self.current_page}',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # 如果获取到了CSRF令牌，添加到请求头中
            if csrf_token:
                headers['X-CSRF-Token'] = csrf_token
            
            # 构建请求体数据
            current_time = int(datetime.datetime.now().timestamp() * 1000)
            data = {
                'q': self.current_query,
                'sortType': 'updated_at',
                'page': str(self.current_page),
                'pageSize': '54',
                'sType': '',
                'fromCollection': '-1',
                'fills': '',
                't': str(current_time)
            }
            
            # 如果获取到了ctoken，添加到请求体中
            if ctoken:
                data['ctoken'] = ctoken
            
            # 使用会话发送POST请求，这样可以保持cookie
            response = session.post(api_url, headers=headers, data=data)
            response.raise_for_status()
            
            # 记录响应状态和内容
            logging.info(f"响应状态码: {response.status_code}")
            logging.info(f"响应内容长度: {len(response.text)} 字节")
            
            # 将完整响应保存到单独的文件中
            json_file = os.path.join(log_dir, f'response_{self.current_query}_{self.current_page}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logging.info(f"完整响应已保存到: {json_file}")
            
            # 尝试解析JSON响应
            try:
                json_data = response.json()
                logging.info(f"JSON解析成功，响应结构: {list(json_data.keys())}")
                
                # 详细记录JSON结构和内容
                if 'code' in json_data:
                    logging.info(f"响应code值: {json_data['code']}")
                if 'message' in json_data:
                    logging.info(f"响应message值: {json_data['message']}")
                if 'data' in json_data:
                    logging.info(f"data字段包含的键: {list(json_data['data'].keys()) if isinstance(json_data['data'], dict) else '非字典类型'}")
                    if isinstance(json_data['data'], dict) and 'icons' in json_data['data']:
                        logging.info(f"icons数量: {len(json_data['data']['icons'])}")
                
            except Exception as json_error:
                logging.error(f"JSON解析失败: {str(json_error)}")
                self.clear_icons()
                error_label = QLabel(f"解析响应数据失败: {str(json_error)}")
                error_label.setAlignment(Qt.AlignCenter)
                self.icons_layout.addWidget(error_label, 0, 0)
                return
            
            # 清除加载标签
            self.clear_icons()
            
            # 检查API响应是否成功 - 修改判断逻辑
            # 原来的判断条件是 if json_data.get('code', 0) != 0:
            # 修改为判断code是否等于200
            if json_data.get('code') != 200:
                # 获取错误信息
                error_msg = json_data.get('message', '未知错误')
                logging.error(f"API返回错误: code={json_data.get('code', '缺失')}, message={error_msg}")
                
                no_results = QLabel(f"请求失败: {error_msg}")
                no_results.setAlignment(Qt.AlignCenter)
                self.icons_layout.addWidget(no_results, 0, 0)
                self.prev_button.setEnabled(self.current_page > 1)
                self.next_button.setEnabled(False)
                return
            
            # 获取图标数据
            if 'data' not in json_data:
                logging.error("响应中缺少'data'字段")
                self.icons_layout.addWidget(QLabel("响应数据格式错误: 缺少'data'字段"), 0, 0)
                return
                
            # 检查icons字段
            if 'icons' not in json_data['data'] or not isinstance(json_data['data']['icons'], list):
                logging.error("响应中缺少有效的'data.icons'字段")
                self.icons_layout.addWidget(QLabel("响应数据格式错误: 缺少有效的'icons'字段"), 0, 0)
                return
                
            icons_data = json_data['data']['icons']
            
            logging.info(f"找到的图标数量: {len(icons_data)}")
            
            if not icons_data:
                no_results = QLabel("没有找到匹配的图标")
                no_results.setAlignment(Qt.AlignCenter)
                self.icons_layout.addWidget(no_results, 0, 0)
                self.prev_button.setEnabled(self.current_page > 1)
                self.next_button.setEnabled(False)
                return
                
            # 显示图标
            row, col = 0, 0
            max_cols = 6  # 每行显示的图标数量
            
            for icon in icons_data:
                # 获取SVG内容
                svg_content = icon.get('show_svg')
                if not svg_content:
                    logging.warning(f"图标缺少SVG内容: {icon}")
                    continue
                
                # 获取图标名称
                icon_name = icon.get('name', "未命名图标")
                
                # 创建图标小部件
                icon_widget = SvgIconWidget(svg_content, icon_name)
                self.icons_layout.addWidget(icon_widget, row, col)
                
                # 更新行列位置
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # 获取分页信息
            total = json_data.get('data', {}).get('count', 0)
            total_pages = (total + 53) // 54  # 每页54个图标，计算总页数
            
            # 启用/禁用分页按钮
            self.prev_button.setEnabled(self.current_page > 1)
            self.next_button.setEnabled(self.current_page < total_pages)
            
        except Exception as e:
            self.clear_icons()
            error_message = f"加载图标时出错: {str(e)}"
            logging.error(error_message, exc_info=True)
            error_label = QLabel(error_message)
            error_label.setAlignment(Qt.AlignCenter)
            self.icons_layout.addWidget(error_label, 0, 0)

    def clear_icons(self):
        # 清除所有图标
        while self.icons_layout.count():
            item = self.icons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = IconDownloader()
    window.show()
    sys.exit(app.exec_())