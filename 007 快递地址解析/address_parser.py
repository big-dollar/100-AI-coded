import pandas as pd
import os
import cpca

def process_excel(file_path):
    """处理Excel文件，解析地址并更新省市信息"""
    try:
        # 读取Excel文件，指定列名
        df = pd.read_excel(file_path, dtype=str)
        
        # 将列标识转换为列名
        df.rename(columns={
            df.columns[5]: '地址',  # F列
            df.columns[6]: '省',   # G列
            df.columns[7]: '市'    # H列
        }, inplace=True)
        
        # 使用cpca解析所有地址
        addresses = df['地址'].tolist()
        parsed_locations = cpca.transform(addresses)
        
        # 更新省市信息
        for index, row in df.iterrows():
            # 只有在原值为空时才更新
            if pd.isna(df.at[index, '省']):
                df.at[index, '省'] = parsed_locations.iloc[index]['省']
            if pd.isna(df.at[index, '市']):
                df.at[index, '市'] = parsed_locations.iloc[index]['市']
        
        # 保存更新后的Excel文件
        output_file = os.path.splitext(file_path)[0] + '_已解析.xlsx'
        df.to_excel(output_file, index=False)
        print(f"处理完成，结果已保存至: {output_file}")
        return True
    
    except Exception as e:
        print(f"处理Excel文件时出错: {str(e)}")
        return False

if __name__ == "__main__":
    file_path = r"d:\工作文件\PYTHON程序\快递地址解析\销售订单.xlsx"
    if os.path.exists(file_path):
        process_excel(file_path)
    else:
        print(f"错误：文件 {file_path} 不存在")