import pandas as pd
from applyPtSlOnT1 import applyPtSlOnT1
from mpPandasObj import mpPandasObj

def getEvents(close, tEvents, ptSl, trgt, minRet, numThreads, t1=False):
    """
    计算事件触发的时间点和交易方向，并应用止盈止损规则
    
    参数:
    ----------
    close : pd.Series
        价格序列，通常是资产的收盘价，索引为时间戳
    tEvents : pd.DatetimeIndex
        通过事件过滤器（如CUSUM）识别的事件发生时间点
    ptSl : float
        止盈止损比例（将应用于上下两个方向）
    trgt : pd.Series
        每个时间点的目标阈值（通常是基于波动率计算的）
    minRet : float
        最小收益率阈值，低于此值的事件将被过滤掉
    numThreads : int
        并行计算使用的线程数
    t1 : pd.Series或bool, 可选
        事件的最大持有时间（时间限制）
        - 如果为False，则不设置时间限制
        - 如果为pd.Series，则包含每个事件的最大持有时间
        
    返回:
    ----------
    pd.DataFrame
        包含以下列的DataFrame:
        - 't1': 事件结束时间（可能是止盈、止损或时间限制触发的最早时间）
        - 'trgt': 目标阈值
        - 'side': 交易方向（默认为1，表示多头）
    """
    # 筛选出事件时间点对应的目标阈值
    trgt = trgt.loc[tEvents]
    
    # 过滤掉目标阈值小于最小收益率的事件
    trgt = trgt[trgt > minRet]
    
    # 如果没有提供事件的时间限制，则创建一个包含NaT（Not a Time）的Series
    if t1 is False:
        t1 = pd.Series(pd.NaT, index=trgt.index)
    
    # 创建交易方向Series，默认为1（多头）
    side_ = pd.Series(1, index=trgt.index)
    
    # 合并t1（时间限制）、trgt（目标阈值）和side（交易方向）为一个DataFrame
    # 并删除目标阈值为空的事件
    events = pd.concat({'t1': t1, 'trgt': trgt, 'side': side_}, axis=1).dropna(subset=['trgt'])
    
    # 使用并行处理应用止盈止损规则
    # 注意：这里将ptSl参数转换为[ptSl, ptSl]，表示止盈和止损使用相同的比例
    df0 = mpPandasObj(func=applyPtSlOnT1, pdObj=('molecule', events.index),
                     numThreads=numThreads, close=close, events=events, ptSl=[ptSl, ptSl])
    
    # 更新事件的结束时间t1为以下三个时间点的最早值：
    # 1. 原始设置的时间限制t1
    # 2. 止盈触发时间pt
    # 3. 止损触发时间sl
    # 通过取每行的最小值来实现
    events['t1'] = df0.dropna(how='all').min(axis=1)
    
    # 删除side列，因为在返回的结果中可能不需要该信息
    # 注意：这里的语法可能需要根据pandas版本调整，新版本可能需要使用axis=1
    events = events.drop('side', axis=1)
    
    # 返回处理后的事件DataFrame
    return events