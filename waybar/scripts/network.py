#!/usr/bin/env python

from collections import namedtuple

import psutil
import psutil._common
import logging
import json
import re
import sys
import time


class Configuration(object):
    logger = logging.getLogger(__name__)
    format = "{up} ⇅{down} "
    excluded_interfaces = ["lo*", "tun*"]
    number_padding = 6

counters = \
    namedtuple(
        "counters",
        ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv']
    )


def human_readable_bytes(count: int, configuration: Configuration) -> str:
    count = count / 1024
    for tag in ["kB", "MB", "GB", "TB"]:
        if count < 1024:
            return f"{count:{configuration.number_padding}.1f}{tag}"
        count = count / 1024
    return "∞"


def write_output(data: counters, configuration: Configuration):
    configuration.logger.info('Writing output')
    output = {
        'text': configuration.format.format(
            down=human_readable_bytes(data.bytes_recv if data else 0, configuration),
            up=human_readable_bytes(data.bytes_sent if data else 0, configuration)
        ),
        'class': 'custom-network',
        'alt': 'custom-network'
    }
    sys.stdout.write(json.dumps(output) + '\n')
    sys.stdout.flush()
    

def get_data(configuration: Configuration) -> counters:
    data = psutil.net_io_counters(pernic=True)
    filtered_data = counters(0, 0, 0, 0)
    for interface in data:
        if not any(
                [re.search(pattern, interface) for pattern in configuration.excluded_interfaces]
        ):
            i_data = data[interface]
            filtered_data = \
                counters(
                    filtered_data.bytes_sent + i_data.bytes_sent,
                    filtered_data.bytes_recv + i_data.bytes_recv,
                    filtered_data.packets_sent + i_data.packets_sent,
                    filtered_data.packets_recv + i_data.packets_recv,
                )
    return filtered_data


def main():
    configuration = Configuration()
    old_count = get_data(configuration)
    write_output(None, configuration)
    while True:
        time.sleep(1)
        count = get_data(configuration)
        write_output(
            counters(
                count.bytes_sent - old_count.bytes_sent,
                count.bytes_recv - old_count.bytes_recv,
                count.packets_sent - old_count.packets_sent,
                count.packets_recv - old_count.packets_recv
            ),
            configuration
        )
        old_count = count


if __name__ == "__main__":
    main()
