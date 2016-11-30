def get_lowest_hashes(top=1):
    with open("best_found.txt", 'r') as f:
        return sorted(f)[:top]


if __name__ == "__main__":
    for result in get_lowest_hashes(5):
        block_header_hash, unix_time, nonce = result.strip().split(", ")
        print("hash: {}, unix_time: {}, nonce: {}".format(
            block_header_hash, unix_time, nonce))
