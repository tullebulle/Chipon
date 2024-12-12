import numpy as np

from layers.utils import range_to_bits, ftfp


class Linear:
    @classmethod
    def layer_from(cls, layer, index: int, FW: int):
        return cls(layer.in_features, layer.out_features, layer.weight.detach().numpy().T, layer.bias.detach().numpy(),
                   index, FW)

    def __init__(self, in_features: int, out_features: int, weight: np.ndarray, bias: np.ndarray, index: int, FW: int):
        self.in_features = in_features
        self.out_features = out_features

        self.bias = bias
        self.weight = weight

        self.verify_weights()

        self.name = f'layer_{index}_linear_{str(self.in_features)}_{str(self.out_features)}'
        self.shape = (self.in_features, self.out_features)

        self.in_bits, self.out_bits = None, None
        self.fractional_bits = FW
        self.integer_bits = None

    def __str__(self):
        return f'Linear({self.in_features} -> {self.out_features})'

    def verify_weights(self):
        if self.weight is None:
            raise ValueError('Weight is not defined')

        bias_shape = (self.out_features,)
        weight_shape = (self.in_features, self.out_features)

        if self.weight.shape != weight_shape:
            raise ValueError(f'Weight shape is not correct, expected {weight_shape}, got {self.weight.shape}')

        if self.bias is not None and self.bias.shape != bias_shape:
            raise ValueError(f'Bias shape is not correct, expected {bias_shape}, got {self.bias.shape}')

    def forward_range(self, in_range: np.ndarray):
        out_range = np.array([in_range.T[0] @ self.weight, in_range.T[1] @ self.weight])
        out_range = (out_range + self.bias).T

        self.in_bits = [range_to_bits(*r) + self.fractional_bits for r in in_range]
        self.out_bits = [range_to_bits(*r) + self.fractional_bits for r in out_range]

        self.set_integer_bits()

        return out_range
    
    def set_integer_bits(self):
        self.integer_bits = [bits - self.fractional_bits for bits in self.in_bits]
        return self.integer_bits
    
    def get_adder(self, IW:int, FW:int, in1:str, in2:str, sum:str):
        return f"""
        adder_module #({IW}, {FW}) add_inst_{sum} (.in1({in1}), .in2({in2}), .out({sum}));
        """
    
    def get_multiplier(self, IW:int, FW:int, in1:str, in2:str, product:str):
        return f"""
        multiplier_module #({IW}, {FW}) mult_inst_{product} (.in1({in1}), .in2({in2}), .out({product}));
        """

    def emit(self):
        """
        Emit Verilog code for this layer
        :return: Verilog code
        """

        # add_bias = [f'add{i} = mul{i} + {self.bias[i]};\n' for i in range(self.out_features)]
        add_bias = [self.get_adder(self.integer_bits[i], self.fractional_bits, f"add{self.out_features-1}_term{self.in_features}", f"{ftfp(self.bias[i], self.integer_bits[i], self.fractional_bits) }", f"add_bias{i}") for i in range(self.out_features)]
        multiply_weight = []

        for i in range(self.out_features):
            # multiply_weight.append(f"mul{i} = 0;\n")
            multiply_weight.append(f"assign add{i}_term{0} = {ftfp(0.0, self.integer_bits[i], self.fractional_bits)};\n")
            for j in range(self.in_features):
                mult_term = self.get_multiplier(self.integer_bits[i], self.fractional_bits, f"in{j}", f"{ftfp(self.weight[j][i], self.integer_bits[i], self.fractional_bits)}", f"mul{i}_term{j}")
                add_term = self.get_adder(self.integer_bits[i], self.fractional_bits, f"mul{i}_term{j}", f"add{i}_term{j}", f"add{i}_term{j+1}")
                multiply_weight.append(mult_term)
                multiply_weight.append(add_term)
                # multiply_weight.append(f"mul{i} = mul{i} + in{j} * {self.weight[j][i]};\n")

        in_params = [f"in{i}" for i in range(self.in_features)]
        out_params = [f"out{i}" for i in range(self.out_features)]

        in_definitions = [f"input signed [{self.in_bits[i] - 1}:0] {in_params[i]};\n"
                          for i in range(self.in_features)]

        out_definitions = [f"output signed [{self.in_bits[i] - 1}:0] {out_params[i]};\n"
                           for i in range(self.out_features)]

        mul_definition = [f"wire signed [{self.in_bits[i] - 1}:0] mul{i}_term{j};\n" for i in range(self.out_features) for j in range(self.in_features)]
        add_definition = [f"wire signed [{self.in_bits[i] - 1}:0] add{i}_term{j};\n" for i in range(self.out_features) for j in range(self.in_features+1)]
        bias_definition = [f"wire signed [{self.in_bits[i] - 1}:0] add_bias{i};\n" for i in range(self.out_features)]

        assigns = [f"assign out{i} = add_bias{i};\n" for i in range(self.out_features)]

        return f"""
module {self.name}({",".join(in_params)}, {",".join(out_params)});
    {'    '.join(in_definitions)}
    {'    '.join(out_definitions)}
    {'    '.join(mul_definition)}
    {'    '.join(add_definition)}
    {'    '.join(bias_definition)}
    {'    '.join(multiply_weight)}
    {'    '.join(add_bias)}
        
    
    {'  '.join(assigns)}
endmodule
"""
