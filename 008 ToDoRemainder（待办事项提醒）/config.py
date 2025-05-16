import json
import os

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "reminder_interval": 30,  # 提醒间隔（分钟）
            "last_reminder_time": None  # 上次提醒时间
        }
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_config.copy()
        return self.default_config.copy()

    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def get_reminder_interval(self):
        """获取提醒间隔（分钟）"""
        return self.config.get("reminder_interval", 30)

    def set_reminder_interval(self, minutes):
        """设置提醒间隔（分钟）"""
        self.config["reminder_interval"] = minutes
        self.save_config()

    def get_last_reminder_time(self):
        """获取上次提醒时间"""
        return self.config.get("last_reminder_time")

    def set_last_reminder_time(self, time_str):
        """设置上次提醒时间"""
        self.config["last_reminder_time"] = time_str
        self.save_config() 