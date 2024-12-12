import numpy as np
from layers.utils import range_to_bits

class Conv1D:
    @classmethod
    def layer_from(cls, layer, index: int, num_inputs: int):
        if layer.out_channels != 1 or layer.in_channels != 1:
            raise ValueError('Only single-channel IO is supported at the moment.')
        return cls(
            in_channels=layer.in_channels,
            kernel_size=layer.kernel_size[0],
            weight=layer.weight.detach().numpy()[0][0],
            bias=layer.bias.detach().numpy()[0] if layer.bias is not None else None,
            index=index,
            num_inputs=num_inputs
        )

    def __init__(self, in_channels: int, kernel_size: int, 
                 weight: np.ndarray, bias: float, index: int, num_inputs: int):
        self.in_channels = in_channels
        self.kernel_size = kernel_size
        self.num_inputs = num_inputs
        self.weight = weight
        self.bias = bias
        self.name = f'layer_{index}_conv1d_{in_channels}_{kernel_size}'
        
        self.verify_weights()
        self.in_bits, self.out_bits = None, None
        self.shape = (num_inputs - kernel_size + 1,)  # Output shape

    def __str__(self):
        return f'Conv1D({self.in_channels}->{1}, k={self.kernel_size})'

    def verify_weights(self):
        if self.weight is None:
            raise ValueError('Weight is not defined')
        
        weight_shape = (self.kernel_size, )  # Only 1 output channel
        if self.weight.shape != weight_shape:
            raise ValueError(f'Weight shape is not correct, expected {weight_shape}, got {self.weight.shape}')

    def forward_range(self, in_range: np.ndarray):
        # Calculate worst-case ranges for convolution
        weight_pos = np.maximum(self.weight, 0)
        weight_neg = np.minimum(self.weight, 0)
        
        out_length = self.num_inputs - self.kernel_size + 1
        out_range = np.zeros((out_length, 2))
        
        for i in range(out_length):
            window_range = in_range[i:i + self.kernel_size]
            min_val = np.sum(weight_pos * window_range[:, 0] + weight_neg * window_range[:, 1])
            max_val = np.sum(weight_pos * window_range[:, 1] + weight_neg * window_range[:, 0])
            
            if self.bias is not None:
                min_val += self.bias
                max_val += self.bias
                
            out_range[i] = [min_val, max_val]
        
        self.in_bits = [range_to_bits(*r) for r in in_range]
        self.out_bits = [range_to_bits(*r) for r in out_range]
        
        return out_range

    def emit(self):
        """
        Emit Verilog code for 1D convolution
        """
        in_params = [f"in{i}" for i in range(self.num_inputs)]
        out_params = [f"out{i}" for i in range(self.num_inputs - self.kernel_size + 1)]

        in_definitions = [
            f"input signed [{self.in_bits[i] - 1}:0] {in_params[i]};\n"
            for i in range(self.num_inputs)
        ]

        out_definitions = [
            f"output signed [{self.out_bits[i] - 1}:0] {out_params[i]};\n"
            for i in range(self.num_inputs - self.kernel_size + 1)
        ]

        # Generate multiplication and accumulation logic
        conv_logic = []
        for i in range(self.num_inputs - self.kernel_size + 1):
            conv_logic.append(f"mul{i} = 0;\n")
            for k in range(self.kernel_size):
                weight_val = self.weight[k]
                conv_logic.append(f"mul{i} = mul{i} + {in_params[i + k]} * {weight_val};\n")
            if self.bias is not None:
                conv_logic.append(f"add{i} = mul{i} + {self.bias};\n")

        mul_definitions = [
            f"reg signed [{self.out_bits[i] - 1}:0] mul{i};\n"
            for i in range(self.num_inputs - self.kernel_size + 1)
        ]
        add_definitions = [
            f"reg signed [{self.out_bits[i] - 1}:0] add{i};\n"
            for i in range(self.num_inputs - self.kernel_size + 1)
        ]

        assigns = [f"assign {out_params[i]} = add{i};\n" for i in range(self.num_inputs - self.kernel_size + 1)]

        return f"""
module {self.name}({",".join(in_params)}, {",".join(out_params)});
    {'    '.join(in_definitions)}
    {'    '.join(out_definitions)}
    
    {'    '.join(mul_definitions)}
    {'    '.join(add_definitions)}
        
    always @(*)
    begin
        {'        '.join(conv_logic)}
    end
    {'    '.join(assigns)}
endmodule
""" 