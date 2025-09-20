import pandas as pd


def getTEvents(gRaw, h):
    """
    使用CUSUM (Cumulative Sum)过滤器算法识别价格序列中的显著变化事件
    
    参数:
        gRaw (pandas.Series): 原始价格或收益率序列，索引应为时间戳
        h (float): 阈值参数，用于触发事件的累积变化量临界值
        
    返回:
        pandas.DatetimeIndex: 包含所有触发事件的时间戳索引
        
    算法原理:
        CUSUM过滤器用于检测时间序列中的显著变化点。该算法维护两个累积和:
        1. 正累积和(sPos): 记录正向价格变化的累积值，若变为负则重置为0
        2. 负累积和(sNeg): 记录负向价格变化的累积值，若变为正则重置为0
        
        当任一累积和超过预设阈值(h)时，记录当前时间点为事件点，并重置相应累积和
    """
    # 初始化事件时间戳列表和累积和变量
    tEvents, sPos, sNeg = [], 0, 0
    
    # 计算价格序列的一阶差分（即日收益率或价格变化）
    diff = gRaw.diff()
    
    # 遍历差分序列中的每个时间点（跳过第一个NaN值）
    for i in diff.index[1:]:
        # 更新正累积和和负累积和
        # 正累积和：只累积正向变化，若变为负则重置为0
        # 负累积和：只累积负向变化，若变为正则重置为0
        sPos, sNeg = max(0, sPos + diff.loc[i]), min(0, sNeg + diff.loc[i])
        
        # 当负累积和小于负阈值时，触发看空事件
        if sNeg < -h:
            sNeg = 0  # 重置负累积和
            tEvents.append(i)  # 记录事件时间点
        
        # 当正累积和大于阈值时，触发看多事件
        elif sPos > h:
            sPos = 0  # 重置正累积和
            tEvents.append(i)  # 记录事件时间点
    
    # 将事件时间戳列表转换为pandas的DatetimeIndex格式返回
    return pd.DatetimeIndex(tEvents)