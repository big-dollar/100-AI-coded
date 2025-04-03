import pandas as pd
import os
import cpca
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading

class AddressParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("地址解析工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件选择部分
        self.file_frame = ttk.LabelFrame(self.main_frame, text="选择Excel文件", padding="10")
        self.file_frame.pack(fill=tk.X, pady=10)
        
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(self.file_frame, textvariable=self.file_path_var, width=60)
        self.file_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(self.file_frame, text="浏览...", command=self.browse_file)
        self.browse_button.pack(side=tk.RIGHT, padx=5)
        
        # 列映射部分
        self.mapping_frame = ttk.LabelFrame(self.main_frame, text="列映射设置", padding="10")
        self.mapping_frame.pack(fill=tk.X, pady=10)
        
        # 地址列
        self.address_frame = ttk.Frame(self.mapping_frame)
        self.address_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.address_frame, text="地址列:").pack(side=tk.LEFT, padx=5)
        self.address_col_var = tk.StringVar()
        self.address_col_combo = ttk.Combobox(self.address_frame, textvariable=self.address_col_var, state="readonly", width=30)
        self.address_col_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 省列
        self.province_frame = ttk.Frame(self.mapping_frame)
        self.province_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.province_frame, text="省列:").pack(side=tk.LEFT, padx=5)
        self.province_col_var = tk.StringVar()
        self.province_col_combo = ttk.Combobox(self.province_frame, textvariable=self.province_col_var, state="readonly", width=30)
        self.province_col_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 市列
        self.city_frame = ttk.Frame(self.mapping_frame)
        self.city_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.city_frame, text="市列:").pack(side=tk.LEFT, padx=5)
        self.city_col_var = tk.StringVar()
        self.city_col_combo = ttk.Combobox(self.city_frame, textvariable=self.city_col_var, state="readonly", width=30)
        self.city_col_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 县列
        self.district_frame = ttk.Frame(self.mapping_frame)
        self.district_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.district_frame, text="县/区列:").pack(side=tk.LEFT, padx=5)
        self.district_col_var = tk.StringVar()
        self.district_col_combo = ttk.Combobox(self.district_frame, textvariable=self.district_col_var, state="readonly", width=30)
        self.district_col_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 操作按钮
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        self.process_button = ttk.Button(self.button_frame, text="开始解析", command=self.start_processing)
        self.process_button.pack(side=tk.RIGHT, padx=5)
        
        self.load_columns_button = ttk.Button(self.button_frame, text="加载列名", command=self.load_columns)
        self.load_columns_button.pack(side=tk.RIGHT, padx=5)
        
        # 日志区域
        self.log_frame = ttk.LabelFrame(self.main_frame, text="处理日志", padding="10")
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = ScrolledText(self.log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 数据
        self.df = None
        self.columns = []
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.log("已选择文件: " + file_path)
            self.load_columns()
    
    def load_columns(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("错误", "请先选择Excel文件")
            return
        
        try:
            self.df = pd.read_excel(file_path, dtype=str)
            self.columns = list(self.df.columns)
            
            # 更新下拉框选项
            self.address_col_combo['values'] = self.columns
            self.province_col_combo['values'] = self.columns
            self.city_col_combo['values'] = self.columns
            self.district_col_combo['values'] = self.columns
            
            # 尝试自动选择可能的列
            for col in self.columns:
                if '地址' in col:
                    self.address_col_var.set(col)
                elif '省' in col:
                    self.province_col_var.set(col)
                elif '市' in col:
                    self.city_col_var.set(col)
                elif '县' in col or '区' in col:
                    self.district_col_var.set(col)
            
            self.log(f"成功加载文件，共有 {len(self.columns)} 列")
            self.status_var.set(f"已加载 {len(self.df)} 行数据")
        except Exception as e:
            messagebox.showerror("错误", f"加载Excel文件失败: {str(e)}")
            self.log(f"错误: {str(e)}")
    
    def start_processing(self):
        if self.df is None:
            messagebox.showerror("错误", "请先加载Excel文件")
            return
        
        address_col = self.address_col_var.get()
        province_col = self.province_col_var.get()
        city_col = self.city_col_var.get()
        district_col = self.district_col_var.get()
        
        if not address_col:
            messagebox.showerror("错误", "请选择地址列")
            return
        
        # 禁用按钮，防止重复点击
        self.process_button.configure(state="disabled")
        self.load_columns_button.configure(state="disabled")
        
        # 在新线程中处理，避免界面卡死
        threading.Thread(target=self.process_excel, args=(
            address_col, province_col, city_col, district_col
        )).start()
    
    def process_excel(self, address_col, province_col, city_col, district_col):
        try:
            self.log(f"开始处理数据...")
            self.status_var.set("正在处理...")
            self.progress_var.set(0)
            
            # 使用cpca解析所有地址
            addresses = self.df[address_col].tolist()
            self.log(f"正在解析 {len(addresses)} 条地址...")
            
            # 初始化计数器变量
            province_missing = 0
            city_missing = 0
            district_missing = 0
            
            # 使用更精确的参数进行解析
            parsed_locations = cpca.transform(addresses, pos_sensitive=True)
            self.log("地址解析完成")
            self.progress_var.set(50)
            
            # 直辖市特殊处理
            direct_cities = ['北京', '天津', '上海', '重庆']
            for i, row in parsed_locations.iterrows():
                # 如果省份是直辖市，但市为空，则将市设置为"市辖区"
                if row['省'] in direct_cities:
                    if pd.isna(row['市']):
                        parsed_locations.at[i, '市'] = "市辖区"
                        self.log(f"直辖市特殊处理: 地址={addresses[i]}, 省={row['省']}, 市=市辖区")
            
            # 天津市特殊处理
            for i, loc in enumerate(parsed_locations.itertuples()):
                if getattr(loc, '省') == '天津' and pd.isna(getattr(loc, '区')):
                    # 尝试从原地址中提取区信息
                    address = addresses[i]
                    self.log(f"尝试修复天津地址: {address}")
                    
                    # 天津市的区列表
                    tianjin_districts = [
                        '和平区', '河东区', '河西区', '南开区', '河北区', '红桥区', 
                        '东丽区', '西青区', '津南区', '北辰区', '武清区', '宝坻区',
                        '滨海新区', '宁河区', '静海区', '蓟州区'
                    ]
                    
                    # 尝试匹配区名
                    for district in tianjin_districts:
                        if district in str(address) or district[:-1] in str(address):
                            parsed_locations.at[i, '区'] = district
                            self.log(f"  修复成功: 区={district}")
                            break
            
            # 更新省市县信息
            total_rows = len(self.df)
            for index, row in self.df.iterrows():
                # 更新进度条
                self.progress_var.set(50 + (index / total_rows) * 50)
                self.root.update_idletasks()
                
                # 省份
                if province_col and pd.isna(row[province_col]) and not pd.isna(parsed_locations.iloc[index]['省']):
                    self.df.at[index, province_col] = parsed_locations.iloc[index]['省']
                elif province_col and pd.isna(parsed_locations.iloc[index]['省']):
                    province_missing += 1
                
                # 城市
                if city_col and pd.isna(row[city_col]) and not pd.isna(parsed_locations.iloc[index]['市']):
                    self.df.at[index, city_col] = parsed_locations.iloc[index]['市']
                elif city_col and pd.isna(parsed_locations.iloc[index]['市']):
                    city_missing += 1
                
                # 区县
                if district_col and pd.isna(row[district_col]) and not pd.isna(parsed_locations.iloc[index]['区']):
                    self.df.at[index, district_col] = parsed_locations.iloc[index]['区']
                elif district_col and pd.isna(parsed_locations.iloc[index]['区']):
                    district_missing += 1
            
            # 单独处理直辖市没有解析到市的情况
            if city_col:
                self.log("开始处理直辖市没有市的情况...")
                direct_city_fixed = 0
                
                # 最终检查：确保所有直辖市地址都有市信息
                if province_col and city_col:
                    final_check_count = 0
                    for index, row in self.df.iterrows():
                        if row[province_col] in direct_cities and pd.isna(row[city_col]):
                            self.df.at[index, city_col] = "市辖区"
                            final_check_count += 1
                        
                        if final_check_count > 0:
                            self.log(f"最终检查: 又发现并修复了 {final_check_count} 条直辖市地址")
            
            # 保存更新后的Excel文件
            file_path = self.file_path_var.get()
            output_file = os.path.splitext(file_path)[0] + '_已解析.xlsx'
            self.df.to_excel(output_file, index=False)
            
            self.progress_var.set(100)
            self.log(f"处理完成，结果已保存至: {output_file}")
            
            # 显示未匹配数量
            missing_info = f"解析结果统计:\n"
            if province_col:
                missing_info += f"- 省份: {total_rows - province_missing}/{total_rows} 匹配成功，{province_missing} 条未匹配\n"
            if city_col:
                missing_info += f"- 城市: {total_rows - city_missing}/{total_rows} 匹配成功，{city_missing} 条未匹配\n"
            if district_col:
                missing_info += f"- 区县: {total_rows - district_missing}/{total_rows} 匹配成功，{district_missing} 条未匹配\n"
            
            self.log(missing_info)
            messagebox.showinfo("处理完成", 
                               f"地址解析完成！\n\n{missing_info}\n\n结果已保存至:\n{output_file}")
            
            self.status_var.set("处理完成")
        except Exception as e:
            self.log(f"处理出错: {str(e)}")
            messagebox.showerror("错误", f"处理Excel文件时出错: {str(e)}")
            self.status_var.set("处理出错")
        
        finally:
            # 恢复按钮状态
            self.process_button.configure(state="normal")
            self.load_columns_button.configure(state="normal")
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # 滚动到最新日志

if __name__ == "__main__":
    root = tk.Tk()
    app = AddressParserApp(root)
    root.mainloop()