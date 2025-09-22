def mpSampleTW(t1, numCoEvents, molecule):
    # 目标：计算事件（标签）生命周期内的平均唯一性
    wght = pd.Series(index=molecule)  # 初始化结果Series，索引为待计算的标签（由molecule指定）
    for tIn, tOut in t1.loc[wght.index].iteritems():
        # 遍历每个标签的时间区间 [tIn, tOut]（t1存储每个标签的结束时间tOut，tIn是标签的起始时间）
        # numCoEvents.loc[tIn:tOut]：取出标签生命周期 [tIn, tOut] 内，每个时间点同时存在的标签数
        # .mean()：对这些“同时存在的标签数”取平均，得到“平均同时活跃数”
        # 1. / ...：取倒数，得到“平均唯一性”（呼应 u_{t,i} = 1/c_t 的平均）
        wght.loc[tIn] = 1. / numCoEvents.loc[tIn:tOut].mean()
    return wght  # 返回每个标签的平均唯一性