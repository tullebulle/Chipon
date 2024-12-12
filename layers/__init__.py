from layers import linear, relu, maxpool, conv, sigmoid, linear_frac

Linear = linear.Linear
LinearFrac = linear_frac.Linear
ReLU = relu.ReLU
MaxPool = maxpool.MaxPool
Conv1D = conv.Conv1D
Sigmoid = sigmoid.Sigmoid

__all__ = ["Linear", "ReLU", "MaxPool", "Conv1D", "Sigmoid", "LinearFrac"   ]

