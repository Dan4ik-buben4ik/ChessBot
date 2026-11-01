"""
working on relevant math operations

maybe Direct Spatial Convolution?
"""


import numpy as np
import numpy.fft


# convolve works
def convolve2d(matrice: np.ndarray, kernel: np.ndarray, mode: str):
    m_h, m_w = np.array(matrice.shape)
    k_h, k_w = np.array(kernel.shape)

    full_h = m_h + k_h - 1
    full_w = m_w + k_w - 1

    fft_h = int(next_fast_len(full_h))
    fft_w = int(next_fast_len(full_w))

    fft_shape = (fft_h, fft_w)

    matrice_fft = np.fft.rfft2(matrice, s=fft_shape)
    kernel_fft = np.fft.rfft2(kernel, s=fft_shape)

    matrice_fft *= kernel_fft

    conv_result = np.fft.irfft2(matrice_fft, s=fft_shape)
    if mode == "full":
        return conv_result[:fft_h, :full_w]

    elif mode == "valid":
        valid_h = m_h - k_h + 1
        valid_w = m_w - k_w + 1

        if valid_h <= 0 or valid_w <= 0:
            raise ValueError(" expected the kernel size to be smaller than the matrice in valid mode")

        return conv_result[k_h - 1 : k_h - 1 + valid_h, k_w - 1 : k_w - 1 + valid_w]

    else:
        raise ValueError("Expected type 'full' or 'valid'")

def next_fast_len(target):
    if target <= 0:
        return 0

    # find the maximum hamming primes
    max_2 = int(np.ceil(np.log2(target)))
    max_3 = int(np.ceil(np.log(target) / np.log(3)))
    max_5 = int(np.ceil(np.log(target) / np.log(5)))


    # get the powers of hamming numbers
    p_2 = 2 ** np.arange(max_2 + 1, dtype=np.int64)
    p_3 = 3 ** np.arange(max_3 + 1, dtype=np.int64)
    p_5 = 5 ** np.arange(max_5 + 1, dtype=np.int64)

    # finding all possible hamming numbers
    smooth_numbers = p_2[:, None, None] * p_3[None, :, None] * p_5[None, None, :]
    valid_numbers = smooth_numbers[smooth_numbers >= target]

    return int(np.min(valid_numbers))


# correlate doesnt work yet
def correlate2d(matrice, kernel, mode):
    m_h, m_w = np.array(matrice.shape)
    k_h, k_w = np.array(kernel.shape)

    full_h = m_h + k_h - 1
    full_w = m_w + k_w - 1

    fft_h = int(next_fast_len(full_h))
    fft_w = int(next_fast_len(full_w))

    fft_shape = (fft_h, fft_w)

    matrice_fft = np.fft.rfft2(matrice, s=fft_shape)
    kernel_fft = np.fft.rfft2(kernel[::-1, ::-1], s=fft_shape)

    matrice_fft *= kernel_fft

    conv_result = np.fft.irfft2(matrice_fft, s=fft_shape)
    if mode == "full":
        return conv_result[:full_h, :full_w]

    elif mode == "valid":
        valid_h = m_h - k_h + 1
        valid_w = m_w - k_w + 1

        if valid_h <= 0 or valid_w <= 0:
            raise ValueError(" expected the kernel size to be smaller than the matrice in valid mode")

        return conv_result[k_h - 1: k_h - 1 + valid_h, k_w - 1: k_w - 1 + valid_w]

    else:
        raise ValueError("Expected type 'full' or 'valid'")


