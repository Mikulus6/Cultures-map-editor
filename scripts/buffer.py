from typing import Literal
data_encoding = "cp1252"


class BufferGiver(bytes):
    """Bytes-like class for giving data from bytes object
    in selected portions as for example: numbers, strings, bits."""
    _bits_per_byte = 8

    def __init__(self, sequence: bytes):
        assert isinstance(sequence, bytes) or isinstance(sequence, bytearray)
        self.sequence = bytes(sequence)
        self.offset = 0

    def __repr__(self):
        return str(self.sequence[self.offset:], encoding=data_encoding)

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.sequence) - self.offset

    def __bytes__(self):
        return self.sequence[self.offset:]

    def bytes(self, length):
        self.offset += length
        if self.offset > len(self.sequence): raise IndexError  # noqa: E701
        return self.sequence[self.offset - length: self.offset]

    def unsigned(self, length):
        return int.from_bytes(self.bytes(length), byteorder="little")

    def signed(self, length):
        value_limit = 2 ** (self.__class__._bits_per_byte * length)
        return (self.unsigned(length) + value_limit // 2) % value_limit - value_limit // 2

    def string(self, length, *, encoding=data_encoding):
        return str(self.bytes(length), encoding=encoding)

    def binary(self, length, *, byteorder: Literal["big", "little"] = "big"):
        data = bin(int.from_bytes(self.bytes(length), byteorder=byteorder))[2:]
        return "0" * ((length * self.__class__._bits_per_byte) - len(data)) + data

    def iterable(self, length):
        return [self.unsigned(1) for _ in range(length)]

    def skip(self, n: int):
        self.offset += n
        if self.offset > len(self.sequence): raise IndexError  # noqa: E701

    def skip_to(self, n: int):
        self.offset = n
        if self.offset > len(self.sequence): raise IndexError  # noqa: E701


class BufferTaker(bytes):
    """Bytes-like class for taking data to bytes object
    in selected portions as for example: numbers, strings, bits."""
    _bits_per_byte = 8

    def __init__(self):
        self.sequence = b""

    def __repr__(self):
        return str(self.sequence, encoding=data_encoding)

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.sequence)

    def __bytes__(self):
        return self.sequence

    def bytes(self, item: bytes):
        self.sequence += item

    def unsigned(self, item: int, *, length):
        self.bytes(item.to_bytes(byteorder="little", length=length, signed=False))

    def signed(self, item: int, *, length):
        self.bytes(item.to_bytes(byteorder="little", length=length, signed=True))

    def string(self, item: str):
        self.sequence += bytes(item, encoding=data_encoding)

    def iterable(self, item):
        for byte in item:
            self.sequence += int.to_bytes(byte, length=1)

    def binary(self, item: str):
        # Works only for big endian encoding.
        assert len(item) % self.__class__._bits_per_byte == 0
        for counter in range(len(item) // 8):
            self.unsigned(int(item[counter * 8: (counter + 1) * 8], 2), length=1)
