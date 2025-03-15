import sys
import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, QScrollArea, 
                            QGridLayout, QLabel, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QByteArray, QBuffer, QSize, QRect, QRectF
from PyQt5.QtSvg import QSvgRenderer
import logging
import datetime

class SvgIconWidget(QWidget):
    def __init__(self, svg_content, icon_name, parent=None):
        super().__init__(parent)
        self.svg_content = svg_content
        self.icon_name = icon_name
        self.setFixedSize(100, 120)
        self.setCursor(Qt.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # 绘制SVG图标
        renderer = QSvgRenderer(QByteArray(self.svg_content.encode()))
        icon_rect = QSize(80, 80)
        x = (self.width() - icon_rect.width()) // 2
        y = 5
        # 将 QRect 修改为 QRectF
        renderer.render(painter, QRectF(x, y, icon_rect.width(), icon_rect.height()))
        
        # 绘制图标名称
        painter.setPen(Qt.black)
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        text_rect = QRect(5, 85, 90, 30)
        painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, self.icon_name)
        
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

# 设置日志
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'icon_search_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class IconDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_page = 1
        self.current_query = ""
        
    def initUI(self):
        self.setWindowTitle('如席矢量图标下载工具')
        self.setGeometry(100, 100, 800, 600)
        
        # 主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入关键词搜索图标...')
        self.search_input.returnPressed.connect(self.search_icons)
        
        self.search_button = QPushButton('搜索')
        self.search_button.clicked.connect(self.search_icons)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        main_layout.addLayout(search_layout)
        
        # 图标显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.icons_container = QWidget()
        self.icons_layout = QGridLayout(self.icons_container)
        self.icons_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.icons_container)
        main_layout.addWidget(self.scroll_area)
        
        # 分页控制
        pagination_layout = QHBoxLayout()
        
        self.prev_button = QPushButton('上一页')
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)
        
        self.page_label = QLabel('第1页')
        self.page_label.setAlignment(Qt.AlignCenter)
        
        self.next_button = QPushButton('下一页')
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        
        main_layout.addLayout(pagination_layout)
        
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