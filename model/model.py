from typing import List

import numpy as np
import torch
from torch import nn
import random
import layers
from model.constants import test_bench_template
from layers.utils import ftfp


class Model:
    def __init__(self, model: nn.Sequential):
        self.model = model
        self.layers = []
        # make seed random
        self.seed = 50
        self.FW = 12
        random.seed(self.seed)
        # first layer is always linear
        self.num_in = layers.Linear.layer_from(self.model[0], 0).shape[0]
        self.parse_layers()
        self.num_out = self.layers[-1].shape[-1]
        self.random_test_inputs = [random.random() for _ in range(self.num_in)]
        self.random_int_test_inputs = [random.randint(0, 5) for _ in range(self.num_in)]

    def __str__(self):
        return '\n'.join(str(layer) for layer in self.layers)
    
    def get_out_features(self, layer):
        try:
            return layer.out_features
        except:
            return 1

    def parse_layers(self):
        i=0
        for layer in self.model:
            if isinstance(layer, nn.Linear):
                self.layers.append(layers.Linear.layer_from(layer, i))
            elif isinstance(layer, nn.ReLU):
                self.layers.append(layers.ReLU(self.get_out_features(self.model[i - 1]), i))
            elif isinstance(layer, nn.MaxPool1d):
                self.layers.append(layers.MaxPool(self.get_out_features(self.model[i - 1]), i, pool_size=layer.kernel_size))
            elif isinstance(layer, nn.Conv1d):
                num_inputs = self.get_out_features(self.layers[i - 1])
                self.layers.append(layers.Conv1D.layer_from(layer, i, num_inputs))
            elif isinstance(layer, nn.Sigmoid):
                self.layers.append(layers.Sigmoid(self.get_out_features(self.model[i - 1]), i))
            elif isinstance(layer, nn.Unflatten) or isinstance(layer, nn.Flatten):
                i = i - 1
            else:
                raise ValueError(f'Unknown layer type {layer}')
            i += 1

    def forward_range(self, ranges: List[List[float]]):
        start = np.array(ranges)

        for layer in self.layers:
            start = layer.forward_range(start)

    def get_vars(self, test_bench=False):
        in_params = [f"in{i}" for i in range(self.layers[0].shape[0])]
        out_params = [f"out{i}" for i in range(self.layers[-1].shape[-1])]

        if test_bench:
            in_definitions = [f"    reg signed [{self.layers[0].in_bits[i] - 1}:0] {in_params[i]};"
                              for i in range(self.layers[0].shape[0])]
            out_definitions = [f"    wire signed [{self.layers[-1].out_bits[i] - 1}:0] {out_params[i]};"
                               for i in range(self.layers[-1].shape[-1])]
            sep_str_in = '"' + (f'%0d,'*self.layers[0].shape[0])[:-1] + '", '
            sep_str_out = '"' + (f'%0d,'*self.layers[-1].shape[-1])[:-1] + '", '
            file_in_str = sep_str_in + ', '.join([f'{in_params[i]}' for i in range(self.layers[0].shape[0])])
            file_out_str = sep_str_out + ', '.join([f'{out_params[i]}' for i in range(self.layers[-1].shape[-1])])

            return in_params, out_params, in_definitions, out_definitions, file_in_str, file_out_str

        else:
            in_definitions = [f"    input signed [{self.layers[0].in_bits[i] - 1}:0] {in_params[i]};"
                              for i in range(self.layers[0].shape[0])]
            out_definitions = [f"    output signed [{self.layers[-1].out_bits[i] - 1}:0] {out_params[i]};"
                               for i in range(self.layers[-1].shape[-1])]
            
        return in_params, out_params, in_definitions, out_definitions


    def emit(self):
        out = ["`timescale 1ns / 1ps"]
        in_params, out_params, in_definitions, out_definitions = self.get_vars()
        top = [
            f"module top({','.join(in_params)}, {','.join(out_params)});",
            *in_definitions,
            *out_definitions,
        ]
        in_wires = in_params
        out_wires = []
        for i, layer in enumerate(self.layers):
            out.append(layer.emit())
            out_wires = []
            for j in range(layer.shape[-1]):
                top.append(f"    wire [{layer.out_bits[j] - 1}:0] layer_{i}_out_{j};")
                out_wires.append(f"layer_{i}_out_{j}")
            top.append(f"    {layer.name} layer_{i}({','.join(in_wires)}, {','.join(out_wires)});")
            in_wires = out_wires
        assigns = [f"    assign out{i} = {out_wire};" for i, out_wire in enumerate(out_wires)]
        top.extend(assigns)
        top.append("endmodule")
        out.append('\n'.join(top))

        return '\n'.join(out)

    def emit_test_bench(self):
        in_params, out_params, in_definitions, out_definitions, file_in_str, file_out_str = self.get_vars(test_bench=True)
        # int_bits =  self.layers[0].integer_bits
        assigns = [f"        assign {in_params[i]} = {self.random_int_test_inputs[i]};" for i in range(len(in_params))]

        return test_bench_template.format(
            in_params=', '.join(in_params),
            out_params=', '.join(out_params),
            in_definitions='\n    '.join(in_definitions),
            out_definitions='\n    '.join(out_definitions),
            assignments='\n'.join(assigns),
            file_in_str=file_in_str,
            file_out_str=file_out_str,
        )
