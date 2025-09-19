import numpy as np


def pcaWeights(cov,riskDist=None,riskTarget=1):
    #Followint the riskAlloc distribution, match riskTarget
    eVal,eVec = np.linalg.eigh(cov)
    indices=eVal.argsort()[::-1]
    eVal,eVec = eVal[indices],eVec[:,indices]
    if riskDist is None:
        riskDist=np.zeros(cov.shape[0])
        riskDist[-1]=1.
    loads = riskTarget*(riskDist/eVal)**.5
    wghts=np.dot(eVec,np.reshape(loads,(-1,1)))
    return wghts
