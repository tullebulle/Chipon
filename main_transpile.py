import torch
from torch import nn
from model.model import Model
import random


def make_model():
    simple_model = nn.Sequential(
        nn.Linear(5, 5),
        nn.Unflatten(1, (1, 5)),   # Add a channel dimension: (batch_size, 1, 5)
        nn.Conv1d(1, 1, 3),
        nn.Flatten(1),             # Flatten back to 2D for Linear: (batch_size, 3)
        nn.Linear(3, 1),
        nn.ReLU(),
        # nn.Sigmoid(),
    )

    # random.seed(42)
    torch.manual_seed(12)
    # # set random weights and biases
    for layer in simple_model:
        if isinstance(layer, nn.Linear):
            # change to integer weights and biases
            layer.weight = nn.Parameter(torch.randint(0, 10, (layer.out_features, layer.in_features), dtype=torch.int32), requires_grad=False)
            layer.bias = nn.Parameter(torch.randint(0, 10, (layer.out_features,), dtype=torch.int32), requires_grad=False)
        elif isinstance(layer, nn.Conv1d):
            layer.weight = nn.Parameter(torch.randint(0, 10, (1, 1, layer.kernel_size[0]), dtype=torch.int32), requires_grad=False)
            # print("weight", layer.weight)
            layer.bias = nn.Parameter(torch.randint(0, 10, (1,), dtype=torch.int32), requires_grad=False)
            # print("bias", layer.bias)

    # simply testing if the model is valid
    simple_model.eval()
    input_shape = simple_model[0].in_features
    inputs = [random.randint(0, 5) for _ in range(input_shape)]
    with torch.no_grad():
        try:
            simple_model(torch.tensor([inputs], dtype=torch.int32))
        except Exception as e:
            raise RuntimeError("Error when defining your PyTorch model: " + str(e))
    
    model = Model(simple_model)
    model.forward_range([[-100.0, 100.0] for _ in range(simple_model[0].in_features)])
    

    return model

def generate_verilog(model: Model):
    code = model.emit()
    with open('output_files/test.v', 'w') as f:
        f.write(code)

    with open('output_files/test_tb.v', 'w') as f:
        f.write(model.emit_test_bench())


if __name__ == '__main__':
    model = make_model()
    generate_verilog(model)
