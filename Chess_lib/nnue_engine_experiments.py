#TODO: write a NNue evaluator

# Half KA v2


"""
Plan: To create a complex NNUE evaluation function

Step 1: Infrastructure
- return: positive is good for the white, negative is bad for the white
- Board.nnue_state to hold the white and black accumulates separately
- create a base function for the state (build_accumulator)

Step 2: small nn
- get the hang of it and prove that it works
- size nn: 128 -> 32 -> 32 -> 1
- feature = piece + square
- total 768 possible features (as 12 pieces x 64 squares)
- board -> feature -> accumulator -> nn -> score pipeline

Step 3: accumulator on go
- make the accumulator updatable by move (so no re-computing)
- goal board.nnue == build_accumulator

Step 4: Half KP
- add the king position into the picture
- so feature = king square (opposite) + piece type + piece color + square
- 64 x 64 x 6 x 2 features (keep the pawns separate)

------------ working engine ----------------

Step 5: Half KA
- add the relevance to both kings
- thus 2 accumulates and 2x the features


Step 6: Contextual features
- keep a few features
- Half KA features, Ray features, Pin features, Attack/defence features?, king safety features
- the accumulator becomes a giant summ with a weight

Step 7: Pawn structure
- white + black pawns form features using a ML that would generate a 128 vector of features
- later turn it into an encoder
- would only be updates when a pawn moves

Step 8: Combine Everything
- combine everything
- decide if some should be concatenated or added

Step 9: experiment with the NNue
- maybe do the different sizes of layers

Step 10: Training
- train the model using top evaluations and positions from chess com
- or set up for alpha-zero type search trees
- use mcts and self-play for training

Step 11: add everything to the engine
"""

"""
Extended steps:

Step 6: Contextual features
- keep a few features
- the accumulator becomes a giant summ with a weight

features to add
- pins
- castling right (4 neurons) * 
- ep file (8 neurons or 1 if using activation) * 
- checks
- pawn structure (1 neuron) * 
- game state -> internally like stockfish

layers wise
* external layer
- castling (4)
- ep (8 by file)

128 vector
- checks - key: Color | piece type | square
- pinned - key: Color | piece type | from sq | to square
- pinner - key: Color | piece type | from square | to square

- for a ray? Positional Polynomial Hashing (If you must use a single math formula).

pawn structure -> external ml

game state -> internal layer

"""
import abc
import numpy as np
import numpy.random


from .util import *
from .loader import Board


""" Plan for tmrw
Step 7: Pawn structure

- custom convolution function
- custom correlation function
- cnn
- leaking relu for activation
- white + black pawns form features using a ML that would generate a 128 vector of features
- later turn it into an encoder
- would only be updates when a pawn moves


 + internal game state 
 + castling (4 neurons)
 + ep (8 neurons)
"""



class Layer(abc.ABC):
    input = None
    output = None
    def forward(self, input_vector): ...

    def backward(self, output_grad_vector, learning_rate): ...

    @classmethod
    def from_size(cls, input_size, output_size): ...


class DenseLayer(Layer):
    def __init__(self, weights: np.ndarray, bias):
        self.weights = weights
        self.bias = bias

    def forward(self, input_vector: np.ndarray) -> np.ndarray:
        self.input = input_vector
        return np.dot(self.weights, input_vector) + self.bias

    def backward(self, output_grad_vector: np.ndarray, learning_rate: float) -> np.ndarray:
        self.weights -= np.dot(output_grad_vector, self.input.T) * learning_rate
        self.bias -= output_grad_vector * learning_rate
        return np.dot(self.weights.T, output_grad_vector)

    @classmethod
    def from_size(cls, input_size, output_size):
        return cls(np.random.randn(output_size, input_size), np.random.randn(output_size))


class ActivationLayer(Layer):
    def __init__(self, activation_function, activation_prime):
        self.activation = activation_function
        self.activation_prime = activation_prime

    def forward(self, input_vector):
        self.input = input_vector
        return self.activation(input_vector)

    def backward(self, output_grad_vector, learning_rate):
        return np.multiply(output_grad_vector, self.activation_prime(self.input))


def CReLu(input_vector, c=64):
    return np.clip(input_vector, 0, c)

def CReLu_prime(output_vector, c=64):
    return np.where((output_vector > 0) & (output_vector < c), 1.0, 0.0)


# class PawnStructureNN:
#     """
#     input layer is 128 (64 white, 64 black)
#
#     Outputs a single neuron
#
#
#     """
#     network = [
#         DenseLayer.from_size(128, 64),
#         ActivationLayer(CReLu, CReLu_prime),
#         DenseLayer.from_size(32, 32),
#     ]

class ConvolutionalLayer(Layer):
    def __init__(self, input_dimensions, output_dimensions, kernel_size, kernel_number):

    def forward(self, input_vector):
        pass

    def backward(self, output_grad_vector, learning_rate):
        pass



class EvaluationNNUE:
    network = [
        DenseLayer.from_size(128, 32),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer.from_size(32, 32),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer.from_size(32, 32),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer.from_size(32, 1)
    ]
    input_size = 128
    output_size = 1

    def generate(self, input_vector: np.ndarray):
        if len(input_vector) != self.input_size:
            raise BaseException("wrong input size")
        for layer in self.network:
            input_vector = layer.forward(input_vector)

        return input_vector

    def back_propagation(self, error_gard_vector: np.ndarray, learning_rate: float):
        if len(error_gard_vector) != self.output_size:
            raise BaseException("wrong input size")

        for layer in self.network[::-1]:
            error_gard_vector = layer.backward(error_gard_vector, learning_rate)



