from hasher import running_it
from queue import Queue


def test_a_time_and_nonce(unix_time, nonce):
    """Try hashing the sample block header and
    check if it correctly hashed"""
    oven = Queue()

    running_it(oven, unix_time, nonce, nonce+1)
    # There really should be a small artificial delay
    # to guarentee that running_it has completed
    block_header = oven.get()

    expected_block_header = "000023ada2555379c8e2fc265c33df90fb03fca53ccd0efe0c5984a5f6075c4d"
    return block_header[0] == expected_block_header


if __name__ == "__main__":
    sample_time = 0x4d64fe57
    sample_nonce = 0x66ae0d00
    print("Success" if test_a_time_and_nonce(sample_time, sample_nonce) else "Failure")
