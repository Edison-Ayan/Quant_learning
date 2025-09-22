import pandas as pd
from applyPtSlOnT1 import applyPtSlOnT1
from mpPandasObj import mpPandasObj

def getEvents(close, tEvents, ptSl, trgt, minRet, numThreads, t1=False, side=None):
    """
    计算事件触发的时间点和交易方向，并应用止盈止损规则
    
    该函数是量化交易策略中的关键组件，用于确定何时进入和退出市场，
    通过设置止盈止损条件来控制风险并锁定利润。
    
    参数:
    ----------
    close : pd.Series
        价格序列，通常是资产的收盘价，索引为时间戳
    tEvents : pd.DatetimeIndex
        通过事件过滤器（如CUSUM）识别的事件发生时间点
    ptSl : list 或 tuple
        止盈止损比例列表，包含两个值 [止盈比例, 止损比例]
    trgt : pd.Series
        每个时间点的目标阈值（通常是基于波动率计算的）
    minRet : float
        最小收益率阈值，低于此值的事件将被过滤掉，用于筛选有意义的交易机会
    numThreads : int
        并行计算使用的线程数，用于加速处理大量数据
    t1 : pd.Series或bool, 可选
        事件的最大持有时间（时间限制）
        - 如果为False，则不设置时间限制
        - 如果为pd.Series，则包含每个事件的最大持有时间
    side : pd.Series, 可选
        交易方向序列，1表示多头，-1表示空头
        - 如果为None，则默认为所有交易都是多头
        
    返回:
    ----------
    pd.DataFrame
        包含以下列的DataFrame:
        - 't1': 事件结束时间（可能是止盈、止损或时间限制触发的最早时间）
        - 'trgt': 目标阈值
        - 'side': 交易方向（仅当输入参数side不为None时包含）
    """
    # 筛选出事件时间点对应的目标阈值
    trgt = trgt.loc[tEvents]
    
    # 过滤掉目标阈值小于最小收益率的事件，确保只处理有足够获利潜力的事件
    trgt = trgt[trgt > minRet]
    
    # 如果没有提供事件的时间限制，则创建一个包含NaT（Not a Time）的Series
    if t1 is False:
        t1 = pd.Series(pd.NaT, index=trgt.index)
    
    # 处理交易方向参数
    if side is None:
        # 创建默认的交易方向Series，所有交易都默认为1（多头）
        side_ = pd.Series(1, index=trgt.index)
        # 使用完整的止盈止损比例列表
        ptSl_ = [ptSl[0], ptSl[1]]
    else:
        # 使用提供的交易方向，并确保与事件时间点对齐
        side_ = side.loc[trgt.index]
        # 仅使用止盈止损比例列表的前两个值
        ptSl_ = ptSl[:2]
    
    # 合并t1（时间限制）、trgt（目标阈值）和side（交易方向）为一个DataFrame
    # 并删除目标阈值为空的事件
    events = pd.concat({'t1': t1, 'trgt': trgt, 'side': side_}, axis=1).dropna(subset=['trgt'])
    
    # 使用并行处理应用止盈止损规则
    # 这里调用mpPandasObj函数进行并行计算，提高大规模数据的处理效率
    # applyPtSlOnT1函数负责计算每个事件何时触发止盈或止损
    df0 = mpPandasObj(func=applyPtSlOnT1, pdObj=('molecule', events.index),
                     numThreads=numThreads, close=close, events=events, ptSl=ptSl_)
    
    # 更新事件的结束时间t1为以下三个时间点的最早值：
    # 1. 原始设置的时间限制t1
    # 2. 止盈触发时间pt
    # 3. 止损触发时间sl
    # 通过取每行的最小值来实现 earliest exit
    events['t1'] = df0.dropna(how='all').min(axis=1)
    
    # 如果最初没有指定交易方向（使用默认多头），则在返回结果中删除side列
    if side is None:
        events = events.drop('side', axis=1)
    
    # 返回处理后的事件DataFrame，包含每个事件的结束时间和目标阈值
    return events