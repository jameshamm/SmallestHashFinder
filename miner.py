import argparse
import multiprocessing as mp

from current_time_hex import current_time_in_reversed_hex
from hasher import running_it
from math import ceil
from threading import Thread
from util import write_out


MAX_PROCESSES = 8
# The sentinal to stop the reading thread
STOP = {}


def distribute(unix_time=0x4d64fe57):
    """Run the job over multiple processes
    Returns success when all the processes have stopped and the reading thread terminated

    TODO:
    A process pool might be a more appropiate structure to use here
    Restarting from a partial run (which forces better reporting
        from the processes on progress too)
    """
    try:
        oven = mp.Queue()

        reader = Thread(target=track_best_hash, args=(oven,))

        start, end = 0x00000000, 0xffffffff+1
        workload = ceil((end - start) / MAX_PROCESSES)
        # Divide the workload evenly among all processes
        # There might be a better way to do distribute the work
        # but this translates nicely to highly parallel code

        workers = []

        for chunk in range(start, end, workload):
            p = mp.Process(target=running_it, args=(oven, unix_time, chunk, chunk+workload))
            p.start()
            workers.append(p)

        reader.start()

        for worker in workers:
            worker.join()

        oven.put(STOP)
        reader.join()

        print("All done, everything gracefully stopped")
        return True
    except Exception as e:
        return False


def track_best_hash(oven):
    """Watches the output queue and reports the best hash found for each process
    The global best is stored"""
    best = ("1", "1", "1")
    for attempt in iter(oven.get, STOP):
        print(attempt)
        if attempt[0] < best[0]:
            print("NEW BEST")
            best = attempt

    write_out("best_found.txt", best)


def run_on_everything():
    """Stupidly long exhaustive search of each timestamp

    Note: Since it takes more than a second to exhaust a timestamp (currently)
    This loop will not finish before needing more than a 4 byte timestamp"""
    for unix_time in range(0x00000000, 0xffffffff+1):
        success = distribute(unix_time)
        if not success:
            write_out("ErrorLog.txt", "Failed on {}".format(unix_time))


def hex_int(x):
    return int(x, 16)


if __name__ == "__main__":
    DEFAULT_TIME = hex_int(current_time_in_reversed_hex())
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "TIME",
        help="the unix timestamp in little endian",
        type=hex_int,
        nargs='?',
        default=DEFAULT_TIME)
    args = parser.parse_args()
    distribute(args.TIME)
