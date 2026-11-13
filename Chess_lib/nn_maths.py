"""
working on relevant math operations

maybe Direct Spatial Convolution?
"""


import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def correlate2d(matrice: np.ndarray, kernel: np.ndarray, mode: str = "valid") -> np.ndarray:
    m_h, m_w = matrice.shape
    k_h, k_w = kernel.shape

    if mode == "valid":
        if m_h < k_h or m_w < k_w:
            raise ValueError("Expected the kernel size to be smaller than the matrice in valid mode")
        # Creates a zero-copy view of all (k_h, k_w) patches and contracts with kernel
        windows = sliding_window_view(matrice, (k_h, k_w))
        return np.einsum("ijkl,kl->ij", windows, kernel, optimize=True)

    elif mode == "full":
        pad_h, pad_w = k_h - 1, k_w - 1
        padded = np.pad(matrice, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant")
        windows = sliding_window_view(padded, (k_h, k_w))
        return np.einsum("ijkl,kl->ij", windows, kernel, optimize=True)

    else:
        raise ValueError("Expected type 'full' or 'valid'")


def convolve2d(matrice: np.ndarray, kernel: np.ndarray, mode: str = "valid") -> np.ndarray:
    # Convolution is simply correlation with a 180-degree rotated kernel
    return correlate2d(matrice, kernel[::-1, ::-1], mode=mode)

