"""

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

# Initialization of Random Number Generator for a random initialization of weights and biases
RNG_SEED = 0
RNG = np.random.default_rng(RNG_SEED)


class InvalidShape(BaseException):
    def __init__(self, txt):
        super().__init__(txt)


class Layer(abc.ABC):
    input = None
    output = None
    def forward(self, input_vector): ...

    def backward(self, output_grad_vector, learning_rate): ...

    @classmethod
    def from_size(cls, input_size, output_size): ...


class DenseLayer(Layer):
    def __init__(self, input_size, output_size, from_file=False):
        self.input_shape = (input_size, 1)
        self.output_shape = (output_size, 1)

        if from_file:
            raise NotImplementedError

        global RNG
        self.weights = 2 * RNG.random((output_size, input_size)) - 1
        self.bias = 2 * RNG.random(self.output_shape) - 1

    def forward(self, input_vector: np.ndarray) -> np.ndarray:
        if input_vector.shape != self.input_shape:
            raise InvalidShape(f"Invalid shape for the input. Expected {self.input_shape} but given {input_vector.shape}")
        self.input = input_vector
        return np.dot(self.weights, input_vector) + self.bias

    def backward(self, output_grad_vector: np.ndarray, learning_rate: float) -> np.ndarray:
        if output_grad_vector.shape != self.output_shape:
            raise InvalidShape(f"Invalid gradient shape. Expected {self.output_shape} but given {output_grad_vector.shape}")
        weights_grad = np.dot(output_grad_vector, self.input.T)
        self.weights -= weights_grad * learning_rate
        self.bias -= output_grad_vector * learning_rate
        return np.dot(self.weights.T, output_grad_vector)

    def __repr__(self):
        return f"Dense Layer of input {self.input_shape} and output {self.output_shape}"


class ActivationLayer(Layer):
    def __init__(self, activation_function, activation_prime):
        self.activation = activation_function
        self.activation_prime = activation_prime

    def forward(self, input_vector):
        self.input = input_vector
        return self.activation(input_vector)

    def backward(self, output_grad_vector, learning_rate):
        return np.multiply(output_grad_vector, self.activation_prime(self.input))

    def __repr__(self):
        return f"Activation Layer of function {self.activation.__name__}"


def CReLu(input_vector, c=5000):
    return np.clip(input_vector, -c, c)


def CReLu_prime(output_vector, c=5000):
    return np.where((output_vector > -c) & (output_vector < c), 1.0, 0.0)


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

        global RNG
        self.kernels = 2 * RNG.random(self.kernel_shape) - 1
        self.biases = 2 * RNG.random(self.output_dimensions) - 1 #TODO: consider using only positive bias, as then no point in CReLu



    def forward(self, input_matrice):
        if input_matrice.shape != self.input_dimensions:
            print(input_matrice.shape, self.input_dimensions)
            raise InvalidShape(f"Invalid shape for the input. Expected {self.input_dimensions} but given {input_matrice.shape}")
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
        if output_grad_matrice.shape != self.output_dimensions:
            raise InvalidShape(f"Invalid gradient shape. Expected {self.output_dimensions} but given {output_grad_matrice.shape}")
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
        ReshapeLayer((2, 4, 4), (2 * 4 * 4, 1)),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer(32, 16),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer(16, 8),
    ]

    input_shape = (2, 8, 8)
    output_shape = (8, 1)

    @classmethod
    def forward(cls, input_matrice):
        if input_matrice.shape != cls.input_shape:
            raise InvalidShape(f"Invalid shape for the input. Expected {cls.input_shape} but given {input_matrice.shape}")
        for layer in cls.network:
            input_matrice = layer.forward(input_matrice)

        return input_matrice

    @classmethod
    def backward_propagation(cls, error_gard_vector: np.ndarray, learning_rate: float):
        if error_gard_vector.shape != cls.output_shape:
            raise InvalidShape(f"Invalid shape for the input. Expected {cls.output_shape} but given {error_gard_vector.shape}")

        for layer in cls.network[::-1]:
            error_gard_vector = layer.backward(error_gard_vector, learning_rate)
        return




class EvaluationNNUE:
    network = [
        DenseLayer(276, 32),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer(32, 32),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer(32, 32),
        ActivationLayer(CReLu, CReLu_prime),
        DenseLayer(32, 1)
    ]
    input_shape = (276, 1)
    output_shape = (1, 1)


    @classmethod
    def forward(cls, input_vector):
        if input_vector.shape != cls.input_shape:
            raise InvalidShape(f"Invalid shape for the input. Expected {cls.input_shape} but given {input_vector.shape}")
        for layer in cls.network:
            # print(input_vector[0])
            input_vector = layer.forward(input_vector)

        return input_vector

    @classmethod
    def back_propagation(cls, error_gard_vector: np.ndarray, learning_rate: float, original_position: BitBoard):
        if error_gard_vector.shape != cls.output_shape:
            raise InvalidShape(f"Invalid shape for the input. Expected {cls.output_shape} but given {error_gard_vector.shape}")

        for layer in cls.network[::-1]:
            print(layer)
            error_gard_vector = layer.backward(error_gard_vector, learning_rate)

        cls.parse_and_distribute_error_grad(error_gard_vector, original_position, learning_rate)

    @classmethod
    def build_input(cls, board):
        """
        Builds the input vector for the Neural Network.

        Size (276)
        - white accumulator - 128
        - black accumulator - 128
        - pawn structure neural network - 8
        - castling rights - 4
        - en passant - 8

        :param board:
        :return:
        """

        castling = np.zeros((4, 1))
        for i in scan_backward_bb(board.castling_rights):
            castling[i, 0] = 1
        ep = np.zeros((8, 1))
        if board.ep_square:
            ep[board.ep_square & 7, 0] = 1
        return np.concatenate((board.nnue[0], board.nnue[1], board.pawn_nn, castling, ep))


    @classmethod
    def parse_and_distribute_error_grad(cls, error_grad_vector, board, learning_rate):
        """
        Note: assumes the board is preserved

        :param error_grad_vector:
        :param board:
        :param learning_rate:
        :return:
        """
        arrays_list = np.split(error_grad_vector, [128, 256, 264, 268])

        back_propagation_of_accumulator(board, arrays_list[0], learning_rate)
        back_propagation_of_accumulator(board, arrays_list[1], learning_rate)


        PawnStructCNN.backward_propagation(arrays_list[2], learning_rate)







def squared_error_loss(pred, expected):
    return (expected - pred) ** 2

def squared_error_loss_prime(pred, expected):
    return 2 * (expected - pred)
