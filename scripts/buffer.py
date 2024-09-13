_encoding = "cp1252"


class BufferGiver(bytes):
    """Bytes-like class for giving data from bytes object
    in selected portions as for example: numbers, strings, bits."""
    _bits_per_byte = 8

    def __init__(self, sequence: bytes):
        assert isinstance(sequence, bytes)
        self.sequence = sequence
        self.offset = 0

    def __repr__(self):
        return str(self.sequence[self.offset:])

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

    def string(self, length, *, encoding=_encoding):
        return str(self.bytes(length), encoding=encoding)

    def binary(self, length):
        data = bin(int.from_bytes(self.bytes(length), byteorder="big"))[2:]
        return "0" * ((length * self.__class__._bits_per_byte) - len(data)) + data

    def skip(self, n: int):
        self.offset += n
        if self.offset > len(self.sequence): raise IndexError  # noqa: E701


class BufferTaker(bytes):
    """Bytes-like class for taking data to bytes object
    in selected portions as for example: numbers, strings, bits."""
    _bits_per_byte = 8

    def __init__(self):
        self.sequence = b""

    def __repr__(self):
        return str(self.sequence)

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
        self.sequence += bytes(item, encoding=_encoding)

    def binary(self, item: str):
        assert len(item) % self.__class__._bits_per_byte == 0
        for counter in range(len(item) // 8):
            self.unsigned(int(item[counter * 8: (counter + 1) * 8], 2), length=1)
