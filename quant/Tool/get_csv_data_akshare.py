import pandas as pd
import akshare as ak

def get_stock_data_skshare(stockcodes,start_date="20080101",end_date="20250630"):
    df=[]
    for code in stockcodes:
        stock_zh_a_hist_df = ak.stock_zh_a_hist(
            symbol=str(code),
            period="daily",
            start_date=start_date,
            end_date=end_date
        )
        stock_zh_a_hist_df.columns = ["date","code","open","close","high","low","volume","amount","amplitude","price-limit","change-amount","turn"]
        stock_zh_a_hist_df = stock_zh_a_hist_df.set_index("date")
        df.append(pd.DataFrame(stock_zh_a_hist_df))
    return df

stockcodes = ["600519","002230","000333"]
stockcodeName = ["贵州茅台","科大讯飞","美的集团"]
datas = get_stock_data_skshare(stockcodes)
gzmt = datas[0]
kdxf = datas[1]
meidi = datas[2]

def get_indices_data_akshare(indices_codes, start_date="20000101", end_date="20250630"):
    """获取A股指数的历史交易数据
    
    参数:
        indices_codes (list): 指数代码列表，例如 ["000001", "399001"]
        start_date (str): 开始日期，格式为 "YYYYMMDD"，默认为 "20000101"
        end_date (str): 结束日期，格式为 "YYYYMMDD"，默认为 "20250630"
    
    返回:
        list: 包含各指数数据的DataFrame列表
    """
    df = []
    for code in indices_codes:
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
        df.append(pd.DataFrame(index_zh_a_hist_df))
    return df

indices_codes = ["000001","399001","000300"]
indicescodeName = ["上证指数","深圳成分指数","沪深300"]
datas = get_indices_data_akshare(indices_codes)
sh000001 = datas[0]
hs300 = datas[1]
zz500 = datas[2]