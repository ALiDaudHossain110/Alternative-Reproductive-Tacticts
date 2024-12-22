import math
import numpy as np


class NeuralNetwork():
    def __init__(self):
        pass
    # Softmax function
    def softmax(self,x):
        # Subtract the max for numerical stability
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=-1, keepdims=True)
    # ReLU activation function
    def relu(self, x):
        return np.maximum(0, x)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    
    def forward(self, inputs,gene):
        inputs = (inputs - np.min(inputs)) / (np.max(inputs) - np.min(inputs))

        # Compute the raw output by multiplying inputs with gene (weight matrix)
        raw_output = np.dot(inputs, gene)
        
        # Apply the tanh activation function
        # output = np.tanh(raw_output) #soutput should be argmaxfunction
        # output = self.sigmoid(raw_output)
        # output = self.softmax(raw_output)
        output = self.relu(raw_output)

        return output
