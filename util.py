import binascii
import struct
import hashlib


def invert_endian(x):
    return binascii.hexlify(struct.pack("<L", x)).decode()


def reverse_hex(x):
    return binascii.hexlify(binascii.unhexlify(x)[::-1]).decode()


def sha_it(word):
    return hashlib.sha256(word).hexdigest()


def to_padded_hex(x):
    return format(x, '08x')


def write_out(filename, data):
    with open(filename, "a+") as f:
        f.write(", ".join(map(str, data)))
        f.write("\n")
