import struct
import numpy as np

"""
For the files we would assume this structure:

[Header]
    Magic:          4 bytes ("CHNN")
    Version:        uint16
    Number of arrays: uint16

[Arrays]
    For each array:
        Name length:    uint16
        Name:           bytes
        Number of dimensions: uint8
        Shape:          uint32 per dimension
        Data:           float32 values
"""

MAGIC = b"CHNN"
SUPPORTED_VERSIONS = (0,)


def write_to_file(file_name: str | None, version, arrays_dict):
    with open(file_name, "wb") as f:
        # Headers
        f.write(MAGIC)
        f.write(struct.pack("<HH", version, len(arrays_dict)))

        for name, arr in arrays_dict.items():
            arr = np.asarray(arr, dtype="<f4", order="C")

            name_bytes = name.encode("utf-8")
            f.write(struct.pack("<H", len(name)))
            f.write(name_bytes)

            f.write(struct.pack("<B", arr.ndim))
            f.write(struct.pack("<" + "I" * arr.ndim, *arr.shape))
            f.write(arr.tobytes())

def read_file(file_name):
    arrays_dict = {}

    with open(file_name, "rb") as f:
        magic = f.read(4)
        if magic != MAGIC:
            raise ValueError("Wrong NNue file format")

        version, array_count = struct.unpack("<HH", f.read(4))

        if version in SUPPORTED_VERSIONS:
            raise ValueError(f"Unsupported NNue version: {version}")

        # for name, arr in arrays_dict.items():
        #     arr = np.asarray(arr, dtype="<f4", order="C")
        #
        #     name_bytes = name.encode("utf-8")
        #     f.write(struct.pack("<H", len(name)))
        #     f.write(bytes(name))
        #
        #     f.write(struct.pack("<B", arr.ndim))
        #     f.write("<" + "I" * arr.ndim, *arr.shape)
        #     f.write(arr.tobytes())

        for _ in range(array_count):
            name_byte_len = struct.unpack("<H", f.read(2))[0]
            name = f.read(name_byte_len).decode("utf-8")

            dim = struct.unpack("<B", f.read(1))[0]
            shape = struct.unpack("<" + "I" * dim, f.read(4 * dim))

            size = int(np.prod(shape)) # get the size of the array
            data = np.frombuffer(f.read(4 * size), "<f4")

            if data.size != size:
                raise ValueError(f"Truncated array: {name}")

            arrays_dict[name] = data.reshape(shape).copy()
    return arrays_dict
