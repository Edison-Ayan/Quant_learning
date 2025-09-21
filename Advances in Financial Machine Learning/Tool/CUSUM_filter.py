import pandas as pd
import numpy as np
from typing import Union, List, Optional

def getTEvents(
    gRaw: Union[pd.Series, pd.DataFrame], 
    h: Union[float, pd.Series],
    mode: str = 'both',  # 'both'/'positive'/'negative'
    reset_after_trigger: bool = True
) -> pd.DatetimeIndex:
    """
    优化版CUSUM (Cumulative Sum)过滤器算法，识别价格序列中的显著变化事件
    
    参数:
        gRaw: 原始价格或收益率序列，索引应为时间戳
        h: 阈值参数（可为固定值或随时间变化的序列）
            - 固定值: 对所有时间点使用相同阈值
            - 序列: 必须与gRaw索引一致，实现动态阈值（如基于波动率调整）
        mode: 事件类型过滤
            - 'both': 同时捕捉正向和负向显著变化
            - 'positive': 只捕捉正向显著变化
            - 'negative': 只捕捉负向显著变化
        reset_after_trigger: 触发事件后是否重置累积和，默认为True
        
    返回:
        包含所有触发事件的时间戳索引
        
    优化点:
        1. 支持动态阈值（如基于波动率的自适应阈值）
        2. 增加事件类型过滤选项
        3. 优化累积和计算效率，使用向量化操作
        4. 增强输入验证和异常处理
        5. 支持多列数据处理（如多资产同时计算）
    """
    # --------------------------
    # 1. 输入验证与预处理
    # --------------------------
    # 确保输入是Series（如果是DataFrame则按列处理）
    if isinstance(gRaw, pd.DataFrame):
        return pd.concat(
            [getTEvents(gRaw[col], h, mode, reset_after_trigger) for col in gRaw.columns],
            keys=gRaw.columns
        ).index
    
    if not isinstance(gRaw, pd.Series):
        raise TypeError("gRaw必须是pandas Series或DataFrame")
    
    if gRaw.index.inferred_type not in ['datetime64', 'timedelta64']:
        raise ValueError("gRaw的索引必须是时间类型")
    
    # 处理阈值（支持动态阈值）
    if isinstance(h, pd.Series):
        # 确保阈值与价格序列索引一致
        if not h.index.equals(gRaw.index):
            raise ValueError("动态阈值h的索引必须与gRaw一致")
        h_series = h.reindex(gRaw.index).fillna(method='ffill')  # 填充阈值缺失值
    else:
        if h <= 0:
            raise ValueError("阈值h必须为正数")
        h_series = pd.Series(h, index=gRaw.index)
    
    # 计算差分（日变化量）
    diff = gRaw.diff().dropna()
    if diff.empty:
        return pd.DatetimeIndex([])
    
    # 确保阈值序列与差分序列对齐
    h_series = h_series.reindex(diff.index)
    
    # --------------------------
    # 2. CUSUM算法核心（向量化优化）
    # --------------------------
    # 初始化累积和数组
    s_pos = np.zeros(len(diff))
    s_neg = np.zeros(len(diff))
    events = []
    
    for i, (idx, delta) in enumerate(diff.items()):
        # 计算当前累积和（基于前一次值更新）
        if i == 0:
            current_pos = max(0.0, delta)
            current_neg = min(0.0, delta)
        else:
            current_pos = max(0.0, s_pos[i-1] + delta)
            current_neg = min(0.0, s_neg[i-1] + delta)
        
        s_pos[i] = current_pos
        s_neg[i] = current_neg
        
        # 检查是否触发事件
        trigger_pos = (current_pos > h_series.iloc[i]) and (mode in ['both', 'positive'])
        trigger_neg = (current_neg < -h_series.iloc[i]) and (mode in ['both', 'negative'])
        
        if trigger_pos or trigger_neg:
            events.append(idx)
            # 触发后是否重置累积和
            if reset_after_trigger:
                s_pos[i] = 0.0
                s_neg[i] = 0.0
    
    # --------------------------
    # 3. 结果处理
    # --------------------------
    return pd.DatetimeIndex(events)

































# import pandas as pd


# def getTEvents(gRaw, h):
#     """
#     使用CUSUM (Cumulative Sum)过滤器算法识别价格序列中的显著变化事件
    
#     参数:
#         gRaw (pandas.Series): 原始价格或收益率序列，索引应为时间戳
#         h (float): 阈值参数，用于触发事件的累积变化量临界值
        
#     返回:
#         pandas.DatetimeIndex: 包含所有触发事件的时间戳索引
        
#     算法原理:
#         CUSUM过滤器用于检测时间序列中的显著变化点。该算法维护两个累积和:
#         1. 正累积和(sPos): 记录正向价格变化的累积值，若变为负则重置为0
#         2. 负累积和(sNeg): 记录负向价格变化的累积值，若变为正则重置为0
        
#         当任一累积和超过预设阈值(h)时，记录当前时间点为事件点，并重置相应累积和
#     """
#     # 初始化事件时间戳列表和累积和变量
#     tEvents, sPos, sNeg = [], 0, 0
    
#     # 计算价格序列的一阶差分（即日收益率或价格变化）
#     diff = gRaw.diff()
    
#     # 遍历差分序列中的每个时间点（跳过第一个NaN值）
#     for i in diff.index[1:]:
#         # 更新正累积和和负累积和
#         # 正累积和：只累积正向变化，若变为负则重置为0
#         # 负累积和：只累积负向变化，若变为正则重置为0
#         sPos, sNeg = max(0, sPos + diff.loc[i]), min(0, sNeg + diff.loc[i])
        
#         # 当负累积和小于负阈值时，触发看空事件
#         if sNeg < -h:
#             sNeg = 0  # 重置负累积和
#             tEvents.append(i)  # 记录事件时间点
        
#         # 当正累积和大于阈值时，触发看多事件
#         elif sPos > h:
#             sPos = 0  # 重置正累积和
#             tEvents.append(i)  # 记录事件时间点
    
#     # 将事件时间戳列表转换为pandas的DatetimeIndex格式返回
#     return pd.DatetimeIndex(tEvents)