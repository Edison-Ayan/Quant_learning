import os
import pandas as pd
def read_csv(ts_code):
    # 数据文件路径
    csv_path = f'data/{ts_code}_data.csv'
    
    # 检查文件是否存在
    if not os.path.exists(csv_path):
        print(f"错误：数据文件 {csv_path} 不存在。")
        return
    
    # 读取数据
    print(f"正在读取数据文件：{csv_path}")
    df = pd.read_csv(csv_path, parse_dates=['trade_time'], index_col='trade_time')
    
    # 按时间排序
    df = df.sort_index()
    
    print(f"数据形状：{df.shape}")
    print(f"数据时间范围：{df.index.min()} 至 {df.index.max()}")
    
    return df