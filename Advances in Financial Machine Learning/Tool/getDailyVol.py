import pandas as pd


def getDailyVol(close, span0=100):
    """
    计算金融时间序列的日波动率，使用指数加权移动平均标准差（EWM std）
    
    参数:
    close (pandas.Series): 包含价格数据的时间序列，索引为时间戳
    span0 (int, 可选): 指数加权移动平均的时间跨度，默认值为100
    
    返回:
    pandas.Series: 每个时间点对应的波动率估计值，与输入close具有相同的索引
    
    功能说明:
    1. 该函数通过查找每个时间点前一天的位置，计算价格变化率
    2. 对价格变化率应用指数加权移动平均标准差，得到波动率估计
    3. 波动率常用于风险管理、仓位调整和交易信号生成
    """
    # 步骤1: 为每个时间戳寻找对应的前一天位置索引
    # searchsorted函数查找每个索引减去一天后的插入位置
    df0 = close.index.searchsorted(close.index - pd.Timedelta(days=1))
    
    # 步骤2: 过滤掉无效的负值索引
    df0 = df0[df0 >= 0]
    
    # 步骤3: 创建一个Series，索引为原始close的尾部子集，值为对应的前一天索引
    # 这一步确保了我们有完整的时间对齐关系
    df0 = pd.Series(close.index[df0 - 1], index=close.index[close.shape[0] - df0.shape[0]:])
    
    # 步骤4: 计算价格变化率 = (当前价格/前一天价格) - 1
    # 使用loc获取对应索引的价格数据，并计算价格变化百分比
    df0 = close.loc[df0.index] / close.loc[df0.values].values - 1
    
    # 步骤5: 计算指数加权移动平均标准差，得到波动率估计
    # span参数控制平滑程度，值越大，波动率曲线越平滑
    df0 = df0.ewm(span=span0).std()
    
    # 返回波动率序列
    return df0