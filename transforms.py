import numpy as np

def logit(x):
    """
    Logit function

    Args:
    x (TYPE): x

    Returns:
    TYPE: transformed x
    """
    return np.log(x / (1.0 - x))

def invLogit(x):
    """
    Inverse logit function

    Args:
    x (TYPE): x

    Returns:
    TYPE: transformed x
    """
    return 1.0 / (1.0 + np.exp(-x))

def lrBoundedBackward(x, lower, upper):
    """
    Transform from physical parameters bounded in the interval [lower,upper] to transformed (unconstrained) ones
    
    Args:
        x (TYPE): vector of parameters
        lower (float): vector with lower limits
        upper (float): vector with upper limits
    
    Returns:
    TYPE: transformed vector of parameters
    """
    return logit( (x-lower) / (upper - lower) )

def lrBoundedForward(x, lower, upper):
    """
    Transform from transformed (unconstrained) parameters to physical ones bounded in the interval [lower,upper]
    
    Args:
        x (float): vector of transformed parameters
        lower (float): vector with lower limits
        upper (float): vector with upper limits
    
    Returns:
    Float: transformed variables and log Jacobian
    """
    temp = invLogit(x)
    return lower + (upper - lower) * temp, np.log(upper - lower) + np.log(temp) + np.log(1.0 - temp)


def lBoundedBackward(x, lower):
    """
    Transform from physical parameters with lower limit to transformed (unconstrained) ones
    
    Args:
        x (float): vector of parameters
        lower (float): vector with lower limits
    
    Returns:
    Float: transformed vector of parameters
    """
    return np.log(x-lower)

def lBoundedForward(x, lower):
    """
    Transform from transformed (unconstrained) parameters to physical ones with upper limit
    
    Args:
        x (float): vector of transformed parameters
        lower (float): vector with lower limits     
    
    Returns:
    Float: transformed variables and log Jacobian
    """ 
    return np.exp(x) + lower, x

def rBoundedBackward(x, upper):
    """
    Transform from physical parameters with upper limit to transformed (unconstrained) ones
    
    Args:
        x (float): vector of parameters
        upper (float): vector with upper limits
    
    Returns:
    Float: transformed vector of parameters
    """
    return np.log(upper-x)

def rBoundedForward(x, upper):
    """
    Transform from transformed (unconstrained) parameters to physical ones with upper limit
    
    Args:
        x (float): vector of transformed parameters
        upper (float): vector with upper limits
    
    Returns:
    Float: transformed variables and log Jacobian
    """ 
    return upper - np.exp(x), x

def simplexBackward(x):
    """
    Transform from a simplex of dimension K to transformed (unconstrained) parameters
    
    Args:
        x (float): vector of parameters of size K       
    
    Returns:
    Float: transformed vector of parameters
    """
    K = x.shape[0]
    k = np.arange(K-1) + 1
    zk = np.zeros(K-1)
    for i in range(K-1):
        zk[i] = x[i] / (1.0 - np.sum(x[0:i]))
    return logit(zk) - np.log(1.0 / (K-k))

def simplexForward(x):
    """
    Transform from transformed (unconstrained) parameters to physical ones within a simplex. For a simplex in K dimensions,
    we only provide the K-1 dimensional array x
    
    Args:
        x (float): vector of transformed parameters in K-1 dimensions       
    
    Returns:
    Float: transformed variables of size K and log Jacobian
    """ 
    K = x.shape[0] + 1
    k = np.arange(K - 1)+1
    zk = invLogit(x + np.log(1.0 / (K-k)))
    xk = np.zeros(K)
    for i in range(K-1):
        xk[i] = (1.0 - np.sum(xk[0:i])) * zk[i]     
    xk[K-1] = 1.0 - np.sum(xk[0:K-1])
    return xk, np.log(np.sum(xk[0:K-1] * (1.0-zk[0:K-1])))