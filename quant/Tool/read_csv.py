import pandas as pd
import os


def read_stock_csv(file_path, date_column='trade_date', date_format=None):
    """
    读取股票CSV数据文件并进行基本预处理
    
    参数:
        file_path: CSV文件路径
        date_column: 日期列名称，默认为'trade_date'
        date_format: 日期格式，默认为None，由pandas自动推断
        
    返回:
        预处理后的pandas DataFrame
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 读取CSV文件，解析日期列
    df = pd.read_csv(file_path, parse_dates=[date_column], date_format=date_format)
    
    # 设置日期列为索引
    df.set_index(date_column, inplace=True)
    
    # 重命名列以确保与backtrader兼容
    column_mapping = {
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'vol': 'volume'
    }
    
    # 只重命名存在的列
    existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
    df.rename(columns=existing_columns, inplace=True)
    
    # 排序确保日期顺序正确
    df = df.sort_index()
    
    # 移除重复的行
    df = df[~df.index.duplicated(keep='first')]
    
    # 基本数据清洗：删除完全为空的行
    df.dropna(how='all', inplace=True)
    
    return df


def batch_read_stock_csv(file_paths, date_column='trade_date', date_format=None):
    """
    批量读取多个股票CSV文件
    
    参数:
        file_paths: 文件路径列表或字典{股票代码: 文件路径}
        date_column: 日期列名称
        date_format: 日期格式
        
    返回:
        字典{股票代码或文件路径: 预处理后的DataFrame}
    """
    results = {}
    
    if isinstance(file_paths, dict):
        for code, path in file_paths.items():
            results[code] = read_stock_csv(path, date_column, date_format)
    elif isinstance(file_paths, list):
        for path in file_paths:
            # 从文件路径提取股票代码作为键
            code = os.path.basename(path).split('_')[0]
            results[code] = read_stock_csv(path, date_column, date_format)
    
    return results