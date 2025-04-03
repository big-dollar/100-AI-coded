import os
import sys
import subprocess
import argparse

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

# 添加命令行参数解析
def parse_args():
    parser = argparse.ArgumentParser(description="地址解析工具")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--test-tianjin", action="store_true", help="测试天津市地址解析")
    return parser.parse_args()

# 测试天津市地址解析
def test_tianjin_parsing():
    import cpca
    
    print("=== 天津市地址解析测试 ===")
    test_addresses = [
        "天津市和平区南京路89号",
        "天津市河西区友谊路",
        "天津滨海新区大港油田",
        "天津市津南区咸水沽镇",
        "天津市 河东区 津塘路",
        "天津武清开发区",
        "天津市宝坻区大白庄镇",
        "天津市西青经济开发新区王稳庄津淄公路226号嘉民物流中心4b库区"  # 添加问题地址
    ]
    
    print("\n默认参数解析结果:")
    result1 = cpca.transform(test_addresses)
    print(result1)
    
    print("\n位置敏感解析结果:")
    result2 = cpca.transform(test_addresses, pos_sensitive=True)
    print(result2)
    
    # 直辖市特殊处理
    print("\n直辖市特殊处理后的结果:")
    result3 = cpca.transform(test_addresses, pos_sensitive=True)
    # 处理直辖市
    direct_cities = ['北京', '天津', '上海', '重庆']
    for i, row in result3.iterrows():
        if row['省'] in direct_cities and pd.isna(row['市']):
            result3.at[i, '市'] = row['省']
    print(result3)
    
    input("\n按Enter键继续...")

# 运行主程序
if __name__ == "__main__":
    args = parse_args()
    
    if args.test_tianjin:
        test_tianjin_parsing()
    
    if args.debug:
        # 设置环境变量以启用调试模式
        os.environ["ADDRESS_PARSER_DEBUG"] = "1"
        print("调试模式已启用")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "address_parser_gui.py")
    subprocess.call([sys.executable, script_path])