

# Half KA v2


"""

Step 10: Training
- train the model using top evaluations and positions from chess com
- or set up for alpha-zero type search trees
- use mcts and self-play for training

Step 11: add everything to the engine

Step 12:
- rewrite everything to work on the gpu, using opencl and creating class GPUArray
- includes writting a buffer to send the task to gpu in groups

Step 13
- creating a states pool object, that re-uses the board states. Should be linked to a buffer, as per breadth search.
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
# from .loader import Board
from .nn_maths import *


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

# consider static rng later
# SEED = 0

class Layer(abc.ABC):
    input = None
    output = None
    def forward(self, input_vector): ...

    def backward(self, output_grad_vector, learning_rate): ...

    @classmethod
    def from_size(cls, input_size, output_size): ...


class DenseLayer(Layer):
    def __init__(self, input_size, output_size, from_file=False):
        self.input_size = input_size
        self.output_size = output_size

        if from_file:
            raise NotImplementedError

        self.weights = np.random.randn(output_size, input_size)
        self.bias = np.random.randn(output_size)


    def forward(self, input_vector: np.ndarray) -> np.ndarray:
        self.input = input_vector
        return np.dot(self.weights, input_vector) + self.bias

    def backward(self, output_grad_vector: np.ndarray, learning_rate: float) -> np.ndarray:
        self.weights -= np.dot(output_grad_vector, self.input.T) * learning_rate
        self.bias -= output_grad_vector * learning_rate
        return np.dot(self.weights.T, output_grad_vector)

    # @classmethod
    # def from_size(cls, input_size, output_size):
    #     return cls(np.random.randn(output_size, input_size), np.random.randn(output_size))


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
    return np.clip(input_vector, -c, c)

def CReLu_prime(output_vector, c=64):
    return np.where((output_vector > -c) & (output_vector < c), 1.0, 0.0)


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
    def __init__(self, input_dimensions, kernel_size, depth, from_file=None):
        input_depth, input_height, input_width = input_dimensions
        self.depth = depth
        self.input_dimensions = input_dimensions
        self.input_depth = input_depth

        self.output_dimensions = (depth, input_height - kernel_size + 1, input_width - kernel_size + 1)
        self.kernel_shape = (depth, input_depth, kernel_size, kernel_size)

        if from_file:
            raise NotImplementedError

        self.kernels = np.random.randn(*self.kernel_shape)
        self.biases = np.random.randn(*self.output_dimensions)



    def forward(self, input_matrice):
        """
        the formula for forward is Y = X correlate W + B
        """
        self.input = input_matrice
        output = np.copy(self.biases)
        for i in range(self.depth):
            for j in range(self.input_depth):
                output[i] += correlate2d(input_matrice[j], self.kernels[i][j], "valid")
        return output

    def backward(self, output_grad_matrice, learning_rate):
        kernel_gradient = np.zeros(self.kernel_shape)
        input_gradient = np.zeros(self.input_dimensions)
        """
        Y - dE/dY
        K - kernels

        the formula for
        dE/dK = Y correlate X
        dE/dB = Y
        dE/dX = Y concolve K
        """

        for i in range(self.depth):
            for j in range(self.input_depth):
                kernel_gradient[i, j] += correlate2d(self.input[j], output_grad_matrice[i], "valid")
                input_gradient[j] += convolve2d(output_grad_matrice[i], self.kernels[i, j], "full")

        self.kernels -= kernel_gradient * learning_rate
        self.biases -= output_grad_matrice * learning_rate
        return input_gradient


class ReshapeLayer(Layer):
    def __init__(self, input_shape, output_shape):
        self.input_shape = input_shape
        self.output_shape = output_shape

    def forward(self, input):
        # print(input.shape)
        # print(self.output_shape)
        return np.reshape(input, self.output_shape)

    def backward(self, output_grad_vector, learning_rate):
        return np.reshape(output_grad_vector, self.input_shape)


class PawnStructCNN:
    network = [
        ConvolutionalLayer((2, 8, 8), 5, 2),
        ReshapeLayer((2, 4, 4), (2 * 4 * 4,)),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer(32, 16),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer(16, 8),
    ]

    input_shape = (2, 8, 8, )
    output_shape = (8, )

    @classmethod
    def forward(cls, input_matrice):
        for layer in cls.network:
            input_matrice = layer.forward(input_matrice)

        return input_matrice

    @classmethod
    def backward_propagation(cls, error_gard_vector: np.ndarray, learning_rate: float):
        if error_gard_vector.shape != cls.output_shape:
            raise BaseException("wrong input size")

        for layer in cls.network[::-1]:
            error_gard_vector = layer.backward(error_gard_vector, learning_rate)
        return



class AttackersCNN:
    network = [
        ConvolutionalLayer((2, 8, 8), 5, 2),
        ActivationLayer(CReLu, CReLu_prime),
        ReshapeLayer((2, 4, 4), (32,)),
        DenseLayer(32, 16)
    ]
    input_shape = (2, 8, 8,)
    output_shape = (16,)

    @classmethod
    def forward(cls, input_matrice):
        for layer in cls.network:
            input_matrice = layer.forward(input_matrice)

        return input_matrice

    @classmethod
    def back_propagation(cls, error_gard_vector: np.ndarray, learning_rate: float):
        if error_gard_vector.shape != cls.output_shape:
            raise BaseException("wrong input size")

        for layer in cls.network[::-1]:
            error_gard_vector = layer.backward(error_gard_vector, learning_rate)
        return




class EvaluationNNUE:
    network = [
        DenseLayer(292, 32),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer(32, 32),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer(32, 32),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer(32, 1)
    ]
    input_shape = (292, )
    output_shape = (1, )

    @classmethod
    def build_input(cls, board):
        opponent_color = 1 ^ board.turn
        king = board.king_sq[board.turn]
        # attacks_input = bitboards_to_plane(board.attackers_mask(king, opponent_color), 1 << king) # shape 2 supposed to be
        # print(f"attack input: {attacks_input}")
        # print(f"shape: {attacks_input.shape}")
        nn_attackers_array = AttackersCNN.forward(bitboards_to_plane(board.attackers_mask(king, opponent_color), 1 << king))
        # cant concatenate with different dimensions?
        castling = np.zeros(4)
        for i in scan_backward_bb(board.castling_rights):
            castling[i] = 1
        ep = [0 for _ in range(8)]
        if board.ep_square:
            ep[board.ep_square & 7] = 1
        # print(f"dimensions: {board.nnue[0].shape}, {board.nnue[1].shape}, {nn_attackers_array.shape}, {board.pawn_nn.shape}, {castling.shape}")
        return np.concatenate((board.nnue[0], board.nnue[1], nn_attackers_array, board.pawn_nn, castling, ep))

    @classmethod
    def forward(cls, position):
        input_vector = cls.build_input(position)
        if input_vector.shape != cls.input_shape:
            print(f"input vector is of wrong size")
            print(input_vector.shape)
            print(input_vector)
            raise BaseException("wrong input size")
        for layer in cls.network:
            input_vector = layer.forward(input_vector)

        return input_vector

    @classmethod
    def back_propagation(cls, error_gard_vector: np.ndarray, learning_rate: float):
        if len(error_gard_vector) != cls.output_size:
            raise BaseException("wrong input size")

        for layer in cls.network[::-1]:
            error_gard_vector = layer.backward(error_gard_vector, learning_rate)




