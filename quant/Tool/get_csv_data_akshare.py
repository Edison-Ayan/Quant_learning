import akshare as ak
import pandas as pd  # 添加pandas导入
import os  # 添加os模块用于目录操作
import akshare as ak  # 添加akshare库的导入

# 注意：函数名中的'skshare'拼写有误，应为'akshare'
def get_stock_data_skshare(stockcodes, start_date="20080101", end_date="20250630", save_csv=True, output_dir="./data", use_local_data=False):
    """获取A股股票的历史交易数据并可选保存为CSV文件
    
    参数:
        stockcodes (list): 股票代码列表，例如 ["600519", "002230"]
        start_date (str): 开始日期，格式为 "YYYYMMDD"，默认为 "20080101"
        end_date (str): 结束日期，格式为 "YYYYMMDD"，默认为 "20250630"
        save_csv (bool): 是否保存为CSV文件，默认为True
        output_dir (str): CSV文件保存目录，默认为"./data"
        use_local_data (bool): 是否使用本地数据，默认为False
    
    返回:
        list: 包含各股票数据的DataFrame列表，每个DataFrame包含单只股票的历史交易数据
    """
    # 初始化一个空列表，用于存储所有股票的数据
    df = []
    
    # 如果需要保存文件，先确保目录存在
    if save_csv:
        # 检查目录是否存在，如果不存在则创建
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建目录: {output_dir}")
    
    # 遍历股票代码列表，获取每只股票的数据
    for code in stockcodes:
        # 构建本地CSV文件路径
        csv_file = f"{output_dir}\{code}_stock_{start_date}_{end_date}.csv"
        
        # 检查是否使用本地数据或本地已有数据
        if use_local_data or os.path.exists(csv_file):
            try:
                # 尝试从本地加载数据
                stock_zh_a_hist_df = pd.read_csv(csv_file, index_col="date")
                print(f"已从本地加载股票{code}数据")
                df.append(stock_zh_a_hist_df)
                continue
            except Exception as e:
                print(f"从本地加载数据失败: {e}")
        
        try:
            # 使用akshare库获取A股每日历史数据
            stock_zh_a_hist_df = ak.stock_zh_a_hist(
                symbol=str(code),        # 转换为字符串格式的股票代码
                period="daily",          # 周期为日线
                start_date=start_date,   # 开始日期
                end_date=end_date        # 结束日期
            )
            
            # 重命名列名，使其更符合常规命名规范
            stock_zh_a_hist_df.columns = ["date", "code", "open", "close", "high", "low", 
                                         "volume", "amount", "amplitude", "price-limit", 
                                         "change-amount", "turn"]
            
            # 设置日期列为索引，方便后续的时间序列分析
            stock_zh_a_hist_df = stock_zh_a_hist_df.set_index("date")
            
            # 如果需要保存为CSV文件
            if save_csv:
                # 保存为CSV文件，保留日期索引
                stock_zh_a_hist_df.to_csv(csv_file, index=True)
                print(f"股票数据已保存至: {csv_file}")
            
            # 将处理后的DataFrame添加到结果列表中
            df.append(stock_zh_a_hist_df)
        except Exception as e:
            print(f"获取股票{code}数据失败: {e}")
            # 尝试查找其他可能的本地文件格式
            alternative_files = [f for f in os.listdir(output_dir) if code in f]
            if alternative_files:
                try:
                    # 使用第一个找到的包含代码的文件
                    alt_file = os.path.join(output_dir, alternative_files[0])
                    stock_zh_a_hist_df = pd.read_csv(alt_file, index_col=0)
                    print(f"已从本地替代文件{alt_file}加载股票{code}数据")
                    df.append(stock_zh_a_hist_df)
                except Exception as e2:
                    print(f"从替代文件加载数据失败: {e2}")
            else:
                print(f"未找到股票{code}的本地数据文件")
    
    # 返回包含所有股票数据的列表
    return df

# 修改指数数据函数，添加CSV保存功能
def get_indices_data_akshare(indices_codes, start_date="20000101", end_date="20250630", save_csv=True, output_dir="./data", use_local_data=False):
    """获取A股指数的历史交易数据并可选保存为CSV文件
    
    参数:
        indices_codes (list): 指数代码列表，例如 ["000001", "399001"]
        start_date (str): 开始日期，格式为 "YYYYMMDD"，默认为 "20000101"
        end_date (str): 结束日期，格式为 "YYYYMMDD"，默认为 "20250630"
        save_csv (bool): 是否保存为CSV文件，默认为True
        output_dir (str): CSV文件保存目录，默认为"./data"
        use_local_data (bool): 是否使用本地数据，默认为False
    
    返回:
        list: 包含各指数数据的DataFrame列表
    """
    df = []
    
    # 如果需要保存文件，先确保目录存在
    if save_csv:
        # 检查目录是否存在，如果不存在则创建
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建目录: {output_dir}")
    
    for code in indices_codes:
        # 构建本地CSV文件路径
        csv_file = f"{output_dir}\{code}_index_{start_date}_{end_date}.csv"
        
        # 检查是否使用本地数据或本地已有数据
        if use_local_data or os.path.exists(csv_file):
            try:
                # 尝试从本地加载数据
                index_zh_a_hist_df = pd.read_csv(csv_file, index_col="date")
                print(f"已从本地加载指数{code}数据")
                df.append(index_zh_a_hist_df)
                continue
            except Exception as e:
                print(f"从本地加载数据失败: {e}")
        
        try:
            # 获取指数数据
            index_zh_a_hist_df = ak.index_zh_a_hist(
                symbol=str(code),
                period="daily",
                start_date=start_date,
                end_date=end_date
            )
            
            # 动态检查列数并调整列名列表
            # 指数数据通常比股票数据少一列（缺少'price-limit'列）
            if len(index_zh_a_hist_df.columns) == 11:
                # 适用于11列的指数数据
                index_zh_a_hist_df.columns = ["date", "code", "open", "close", "high", "low", 
                                             "volume", "amount", "amplitude", "change-amount", "turn"]
            else:
                # 适用于12列的股票数据格式
                index_zh_a_hist_df.columns = ["date", "code", "open", "close", "high", "low", 
                                             "volume", "amount", "amplitude", "price-limit", 
                                             "change-amount", "turn"]
            
            # 设置日期列为索引
            index_zh_a_hist_df = index_zh_a_hist_df.set_index("date")
            
            # 如果需要保存为CSV文件
            if save_csv:
                # 保存为CSV文件
                index_zh_a_hist_df.to_csv(csv_file, index=True)
                print(f"指数数据已保存至: {csv_file}")
            
            df.append(index_zh_a_hist_df)
        except Exception as e:
            print(f"获取指数{code}数据失败: {e}")
            # 尝试查找其他可能的本地文件格式
            alternative_files = [f for f in os.listdir(output_dir) if code in f]
            if alternative_files:
                try:
                    # 使用第一个找到的包含代码的文件
                    alt_file = os.path.join(output_dir, alternative_files[0])
                    index_zh_a_hist_df = pd.read_csv(alt_file, index_col=0)
                    print(f"已从本地替代文件{alt_file}加载指数{code}数据")
                    df.append(index_zh_a_hist_df)
                except Exception as e2:
                    print(f"从替代文件加载数据失败: {e2}")
            else:
                print(f"未找到指数{code}的本地数据文件")
    return df

# 添加一个测试示例
if __name__ == "__main__":
    # 测试股票数据获取并保存为CSV
    stock_data = get_stock_data_skshare(["600519"], start_date="20230101", end_date="20231231", save_csv=True)
    
    # 测试指数数据获取并保存为CSV
    index_data = get_indices_data_akshare(["000001"], start_date="20230101", end_date="20231231", save_csv=True)