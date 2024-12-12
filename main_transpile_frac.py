import torch
from torch import nn
from model.model_frac import Model
import random


def make_model_frac():
    simple_model = nn.Sequential(
        nn.Linear(5, 1),
        # nn.Linear(2, 1),
        # nn.Unflatten(1, (1, 5)),   # Add a channel dimension: (batch_size, 1, 5)
        # nn.Conv1d(1, 1, 3),
        # nn.Flatten(1),             # Flatten back to 2D for Linear: (batch_size, 3)
        # nn.Linear(3, 1),
        # nn.Sigmoid(),
    )

    # random.seed(42)
    torch.manual_seed(13)
    # # set random weights and biases

    for layer in simple_model:
        if isinstance(layer, nn.Linear):
            layer.weight = nn.Parameter(torch.rand( (layer.out_features, layer.in_features)), requires_grad=False)
            layer.bias = nn.Parameter(torch.rand( (layer.out_features,)), requires_grad=False)
        # elif isinstance(layer, nn.Conv1d):
        #     layer.weight = nn.Parameter(torch.randint(0, 10, (1, 1, layer.kernel_size[0])), requires_grad=False)
        #     layer.bias = nn.Parameter(torch.randint(0, 10, (1,)), requires_grad=False)

    # simply testing if the model is valid
    simple_model.eval()
    input_shape = simple_model[0].in_features
    inputs = [random.randint(0, 5) for _ in range(input_shape)]
    with torch.no_grad():
        try:
            simple_model(torch.tensor([inputs], dtype=torch.float32))
        except Exception as e:
            raise RuntimeError("Error when defining your PyTorch model: " + str(e))
    
    model = Model(simple_model)
    model.forward_range([[-100.0, 100.0] for _ in range(simple_model[0].in_features)])
    

    return model

def generate_verilog(model: Model):
    code = model.emit()
    with open('output_files_frac/test.v', 'w') as f:
        f.write(code)

    with open('output_files_frac/test_tb.v', 'w') as f:
        f.write(model.emit_test_bench())


if __name__ == '__main__':
    model = make_model_frac()
    generate_verilog(model)
