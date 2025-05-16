# 待办事项提醒 (Todo Reminder)

一个基于 PyQt5 开发的待办事项管理工具，支持系统托盘提醒、定时提醒等功能。

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

## ✨ 功能特点

- 📝 待办事项管理
  - 添加、编辑、删除待办事项
  - 设置待办事项的标题、描述和到期时间
  - 标记待办事项为已完成/未完成
  - 支持按到期时间、标题、创建时间排序
  - 支持关键字搜索

- 🔔 提醒功能
  - 系统托盘图标显示未完成事项数量
  - 可配置的定时提醒（1分钟到24小时）
  - 过期事项自动提醒
  - 最小化到系统托盘运行

- 🎨 界面设计
  - 现代化的用户界面
  - 清晰的事项状态显示（未完成、已完成、已过期）
  - 支持快捷键操作
  - 自适应窗口布局

## 📋 系统要求

- Python 3.8 或更高版本
- PyQt5
- SQLite3

## 🚀 安装说明

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/todo-reminder.git
cd todo-reminder
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 💻 使用方法

1. 运行程序：
```bash
python main.py
```

2. 基本操作：
   - 点击"添加新待办"或使用快捷键 `Alt+N` 添加待办事项
   - 双击待办事项或点击"编辑"按钮修改待办事项
   - 点击"标记完成"将事项标记为已完成
   - 点击"显示已完成事项"切换显示状态
   - 使用搜索框搜索待办事项
   - 使用排序下拉框选择排序方式

3. 提醒设置：
   - 在界面顶部设置提醒间隔时间（1-1440分钟）
   - 程序会在系统托盘显示提醒
   - 点击托盘图标可以快速打开主窗口

## 🛠️ 项目结构

```
todo-reminder/
├── main.py              # 程序入口
├── todo_app_qt.py       # 主应用程序类
├── config.py            # 配置管理
├── requirements.txt     # 依赖列表
├── README.md           # 项目说明
├── database/           # 数据库相关
│   └── db_manager.py   # 数据库管理类
└── ui/                 # 界面相关
    ├── main_window_qt.py    # 主窗口
    ├── todo_dialog.py       # 待办事项对话框
    └── tray_icon_qt.py      # 系统托盘图标
```

## ⌨️ 快捷键

- `Alt+N`: 添加新待办事项
- `Enter`: 在搜索框中按回车进行搜索
- `双击`: 编辑选中的待办事项

## 🔧 配置说明

配置文件 `config.json` 包含以下设置：
- `reminder_interval`: 提醒间隔时间（分钟）
- `last_reminder_time`: 上次提醒时间

## 🤝 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📝 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👏 致谢

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI框架
- [SQLite](https://www.sqlite.org/) - 数据库支持

## 📮 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至：centos@126.com

## 🌟 支持项目

如果这个项目对您有帮助，欢迎：
- 给项目点个 Star
- 分享给更多需要的人
- 提交 Issue 或 Pull Request 帮助改进项目 
