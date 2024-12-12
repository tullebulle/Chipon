import numpy as np
from layers.utils import range_to_bits

class MaxPool:
    def __init__(self, shape: int, index: int, pool_size: int = 2):
        self.input_shape = shape
        # Output shape is half the input shape (with pool_size=2)
        self.shape = (shape // pool_size,)
        self.pool_size = pool_size
        self.name = f'layer_{index}_maxpool_{shape}'
        self.in_bits, self.out_bits = None, None

    def __str__(self):
        return f'MaxPool({self.input_shape} -> {self.shape})'

    def forward_range(self, in_range: np.ndarray):
        # Output range will be the same as input range since we're just taking max values
        out_range = np.array([[in_range[i][0], in_range[i][1]] 
                             for i in range(0, self.input_shape, self.pool_size)])
        
        self.in_bits = [range_to_bits(*in_range[i]) for i in range(self.input_shape)]
        # Output bits will be the same as input bits since we're just selecting values
        self.out_bits = [range_to_bits(*out_range[i]) for i in range(self.shape[0])]
        
        return out_range

    def emit(self):
        """
        Emit the Verilog code for max pooling layer
        """
        in_params = [f"in{i}" for i in range(self.input_shape)]
        out_params = [f"out{i}" for i in range(self.shape[0])]

        in_definitions = [f"input [{self.in_bits[i] - 1}:0] {in_params[i]};\n"
                          for i in range(self.input_shape)]
        out_definitions = [f"output reg [{self.out_bits[i] - 1}:0] {out_params[i]};\n"
                           for i in range(self.shape[0])]

        # Generate max pooling logic
        maxpool_code = []
        for i in range(0, self.input_shape, self.pool_size):
            out_idx = i // self.pool_size
            maxpool_code.append(f"""
        // Max pooling for output {out_idx}
        if (in{i} > in{i+1})
            out{out_idx} = in{i};
        else
            out{out_idx} = in{i+1};\n""")

        return f"""
module {self.name}({",".join(in_params)}, {",".join(out_params)});
    {'    '.join(in_definitions)}
    {'    '.join(out_definitions)}
                
    always @(*) 
    begin
        {"        ".join(maxpool_code)}
    end
endmodule
""" 