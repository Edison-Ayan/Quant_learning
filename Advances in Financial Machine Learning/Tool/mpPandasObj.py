# mpPandasObj.py 核心代码（简化版，适用于大多数场景）
import pandas as pd
import numpy as np
import multiprocessing as mp
from typing import Callable, Union, List

def mpPandasObj(
    func: Callable,
    pdObj: Union[pd.Series, pd.DataFrame, List[Union[pd.Series, pd.DataFrame]]],
    numThreads: int = None,
    mpBatches: int = 1,
    linMols: bool = True,
    **kwargs
) -> Union[pd.Series, pd.DataFrame]:
    """
    多进程并行处理Pandas对象
    :param func: 待并行执行的函数（输入为Pandas对象，输出为处理结果）
    :param pdObj: 输入的Pandas Series/DataFrame，或其列表
    :param numThreads: 进程数（默认：CPU核心数）
    :param mpBatches: 批量数（拆分数据的份数，通常设为进程数的2-4倍）
    :param linMols: 是否保持数据索引的连续性
    :param kwargs: 传递给func的额外参数
    :return: 并行处理后的结果（与输入pdObj结构一致）
    """
    # 处理进程数
    if numThreads is None:
        numThreads = mp.cpu_count()
    numThreads = min(numThreads, mp.cpu_count())  # 不超过CPU核心数

    # 处理输入数据（统一转为列表格式）
    if isinstance(pdObj, (pd.Series, pd.DataFrame)):
        pdObj = [pdObj]

    # 拆分数据为批量（避免进程通信开销）
    def splitData(df: Union[pd.Series, pd.DataFrame], batches: int) -> List:
        if batches <= 1:
            return [df]
        # 按索引均匀拆分（保持时间序列连续性）
        splitIdx = np.linspace(0, len(df), batches + 1, dtype=int)[1:-1]
        return np.split(df, splitIdx)

    # 批量拆分所有输入数据
    splitPdObj = []
    for df in pdObj:
        splitPdObj.append(splitData(df, mpBatches * numThreads))
    splitPdObj = list(zip(*splitPdObj))  # 按批量分组

    # 定义多进程任务函数
    def taskFunc(args):
        localDfList, localKwargs = args
        return func(*localDfList, **localKwargs)

    # 执行多进程
    with mp.Pool(numThreads) as pool:
        # 构造任务参数（数据批量 + 额外参数）
        taskArgs = [(dfList, kwargs) for dfList in splitPdObj]
        results = pool.map(taskFunc, taskArgs)

    # 合并结果（恢复原数据结构）
    if linMols:
        if isinstance(results[0], pd.Series):
            return pd.concat(results, ignore_index=False)
        elif isinstance(results[0], pd.DataFrame):
            return pd.concat(results, ignore_index=False)
    return results