import pandas as pd

# 多进程计算并发事件数量函数
def mpNumCoEvents(closeIdx, t1, molecule):
    # 用收盘价索引的最后一个时间点填充t1中的NaN值（处理未结束的事件）
    t1 = t1.fillna(closeIdx.index[-1])
    # 过滤出结束时间在molecule第一个元素时间之后的事件
    t1 = t1[t1 >= molecule[0]]
    # 进一步过滤t1，只保留到molecule中事件的最大结束时间之前的事件
    t1 = t1.loc[:t1[molecule].max()]
    # 在closeIdx中找到t1索引的第一个时间点和最大时间点的位置
    iloc = closeIdx.searchsorted(np.array([t1.index[0], t1.max()]))
    # 创建一个从起始位置到结束位置+1的计数器Series，初始值都为0
    count = pd.Series(0, index=closeIdx[iloc[0]:iloc[1]+1])
    # 遍历每一个事件的进入时间(tIn)和退出时间(tOut)，在对应时间区间内增加计数器
    for tIn, tOut in t1.iteritems(): 
        count.loc[tIn:tOut] += 1
    # 返回从molecule第一个元素时间到molecule中事件最大结束时间的计数结果
    return count.loc[molecule[0]:t1[molecule].max()]