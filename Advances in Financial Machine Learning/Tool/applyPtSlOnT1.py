import pandas as pd


def applyPtSlOnT1(close, events, ptSl, molecule):
    """在事件时间范围内应用止盈(PT)和止损(SL)规则
    
    该函数用于计算金融交易中的止盈和止损触发时间。对于每个事件，它会在指定的时间范围内
    检查价格序列是否达到预设的止盈或止损水平，并记录最早触发的时间点。
    
    参数:
    ----------
    close : pd.Series
        价格序列，通常是资产的收盘价，索引为时间戳
    events : pd.DataFrame
        包含交易事件的DataFrame，必须包含以下列:
        - 't1': 事件的结束时间
        - 'trgt': 目标阈值（通常是价格波动的百分比）
        - 'side': 交易方向（1表示多头，-1表示空头）
    ptSl : 元组
        止盈和止损的倍数，形式为(pt倍数, sl倍数)
        例如(1, 1)表示止盈为目标的1倍，止损也为目标的1倍
    molecule : array-like
        要处理的事件索引子集，用于分批处理大型数据集
    
    返回:
    ----------
    out : pd.DataFrame
        包含以下列的DataFrame:
        - 't1': 原始事件的结束时间
        - 'sl': 止损触发的最早时间点（如果未触发则为NaN）
        - 'pt': 止盈触发的最早时间点（如果未触发则为NaN）
    """
    # 选择指定的事件子集
    events_ = events.loc[molecule]
    # 创建输出DataFrame，复制原始事件的结束时间列
    out = events_[['t1']].copy(deep=True)
    
    # 计算止盈水平
    if ptSl[0] > 0:
        # 止盈水平 = 止盈倍数 * 目标阈值
        pt = ptSl[0] * events_['trgt']
    else:
        # 如果止盈倍数小于等于0，则创建空的Series
        pt = pd.Series(index=events.index)
    
    # 计算止损水平
    if ptSl[1] > 0:
        # 止损水平 = -止损倍数 * 目标阈值（负值表示亏损）
        sl = -ptSl[1] * events_['trgt']
    else:
        # 如果止损倍数小于等于0，则创建空的Series
        sl = pd.Series(index=events.index)
    
    # 遍历每个事件，计算最早触发的止盈或止损时间
    for loc, t1 in events_['t1'].fillna(close.index[-1]).iteritems():
        # 获取从当前位置到结束时间的价格路径
        df0 = close[loc:t1]  # 价格路径
        # 计算相对回报率，并根据交易方向调整
        # events_.at[loc, 'side']获取交易方向(1或-1)
        df0 = (df0 / close[loc] - 1) * events_.at[loc, 'side']  # 调整后的路径回报率
        
        # 记录最早触发止损的时间点
        out.loc[loc, 'sl'] = df0[df0 < sl[loc]].index.min()  # 找到第一个低于止损水平的时间
        # 记录最早触发止盈的时间点
        out.loc[loc, 'pt'] = df0[df0 > pt[loc]].index.min()  # 找到第一个高于止盈水平的时间
    
    # 返回包含止盈止损时间的结果
    return out