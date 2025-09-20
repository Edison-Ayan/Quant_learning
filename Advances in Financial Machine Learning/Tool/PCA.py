import numpy as np


def pcaWeights(cov, riskDist=None, riskTarget=1):
    # Following the riskAlloc distribution, match riskTarget
    eVal, eVec = np.linalg.eigh(cov)  # 计算协方差矩阵的特征值和特征向量
    indices = eVal.argsort()[::-1]    # 获取特征值从大到小排序的索引
    eVal, eVec = eVal[indices], eVec[:, indices]  # 按排序后的顺序重新排列特征值和特征向量
    if riskDist is None:              # 如果没有指定风险分布
        riskDist = np.zeros(cov.shape[0])  # 创建一个全零向量
        riskDist[-1] = 1.             # 将最后一个元素设为1，这意味着默认只在最小的特征值（风险因子）上分配风险
    loads = riskTarget * (riskDist / eVal) ** .5  # 计算载荷向量
    wghts = np.dot(eVec, np.reshape(loads, (-1, 1)))  # 计算最终权重
    return wghts

