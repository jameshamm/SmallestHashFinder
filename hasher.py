"""A block header is 80 bytes and looks like

  Bytes | Descriptions         | Vary?
+-------+----------------------+-------+
|   4   | Block Version Number |   N   |
+-------+----------------------+-------+
|  32   | Previous Block Hash  |   N   |
+-------+----------------------+-------+
|  32   | Merkle Root hash     |   N   |
+-------+----------------------+-------+
|   4   | Unix Timestamp       |   Y   |
+-------+----------------------+-------+
|   4   | Target Threshold     |   N   |
+-------+----------------------+-------+
|   4   | Nonce                |   Y   |
+-------+----------------------+-------+

The search space in this case is 2**32 * 2**32
 = 2**64 possible headers to hash

SHA Implementation details:
    Since the two parts we can adjust are near the end
    (after the first 512 bits) the first 64 bytes of the block can be
    fed into the sha function and every iteration can use this state
    instead of starting afresh.

    In addition, the length of the message is known
    so the 1 + padding 0s could be set beforehand

    Finally for a massive performance gain the check that the first
    2 bytes are set to 0 could be checked in assembly by checking the
    zero flag of the register that produced those bytes

    Unfortunately (or maybe fortunately for my studying)
    as far as I can tell python is to high level to allow these
    micro-optimisations and headaches
"""

import binascii
import hashlib
import struct

from util import invert_endian, reverse_hex, sha_it, to_padded_hex


def running_it(oven, unix_time, start_nonce, end_nonce,
               best=('1', '1', '1')):
    """Goes through a timestamp looking for the lowest hash it can

    Args:
        param oven: a queue to write any new bests found,
        param unix timestamp: 4 byte int from 0x00000000 to 0xffffffff,
        start_nonce: 4 byte int to start at (inclusive),
        end_nonce: 4 byte int to stop at (exclusive),
        best: a tuple (best_hash, unix_timestamp, nonce)
    """
    static_block = get_static_hash_block(unix_time)

    unix_time = to_padded_hex(unix_time)
    last = start_nonce
    count = 0
    try:
        for nonce in range(start_nonce, end_nonce):
            attempt_nonce = binascii.hexlify(struct.pack('>I', nonce))
            attempt_block = static_block.copy()
            attempt_block.update(attempt_nonce)
            attempt_header = attempt_block.hexdigest()
            if attempt_header.startswith('0000'):
                if attempt_header < best[0]:
                    best = (attempt_header, unix_time, attempt_nonce.decode())
                    oven.put(best)

            count += 1
            if count % 0x7fffff == 0:
                print("[{}: {}, {}]".format(unix_time, format(last, '08x'), format(nonce, '08x')))
                last = nonce
    except Exception as e:
        # Throw out anything that might be useful to recover from an unexpected error
        print(e)
        oven.put(best)
        ranges = (best, unix_time, start_nonce, nonce, end_nonce)
        print("Stopping: ", ranges)


def get_static_hash_block(unix_time):
    block_version_num = 2
    transaction = "d"
    index = 3
    branch = [
        "c",
        "fb8e20fc2e4c3f248c60c39bd652f3c1347298bb977b8b4d5903b85055620603",
        "568a301ab7df10a2aa916d2edc73ff7660409b8223d72b8e6b3259ea551b3326",
        "c8dcc7b350de1612febd951b96596648df0ddbd0a1c00fdd92f7b8b32c99b812",
        "c79530adb7ff69abc48a7dba694cb461e047715cbd8addc86c22edd1b2664079"]

    previous_block_hash = "AAAAAAAAAAAAAAAA0000000000000000"
    merkle_root = get_merkle_root(branch, transaction, index)
    unix_time = format(unix_time, '08x')
    target = "AAAAAA18"

    return hashlib.sha256("".join([
        invert_endian(block_version_num), previous_block_hash,
        reverse_hex(merkle_root), unix_time, target]).encode())


def get_merkle_root(branch, transaction, index):
    first = branch[0]
    branch = branch[1:]
    if index & 1:
        root = sha_it((first + transaction).encode())
    else:
        root = sha_it((transaction + first).encode())
    index //= 2
    sides = reversed(format(index, '0{}b'.format(len(branch))))
    # a 0 bit means the current root should go on the left

    for side, node in zip(sides, branch):
        if side == '0':
            root = sha_it((root + node).encode())
        else:
            root = sha_it((node + root).encode())
    return root
