import calendar

from datetime import datetime
from util import reverse_hex


def time_to_reversed_hex(unix_time):
    """Convert the given timestamp to hex and reverse the bytes
    1480445693 -> '583dcefd' '0xfdce3d58"""
    return '0x' + reverse_hex(format(unix_time, '08x'))


def current_time_in_reversed_hex():
    """Return the current time in little endian hex'"""
    now = datetime.utcnow()
    unix_time = calendar.timegm(now.utctimetuple())
    return time_to_reversed_hex(unix_time)


if __name__ == "__main__":
    print(current_time_in_reversed_hex())
