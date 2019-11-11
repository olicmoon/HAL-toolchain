#!/usr/bin/python3
#
# (c)2019 by Lucky Resistor. See LICENSE for details.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import os
import re
import subprocess
import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

assert sys.version_info >= (3, 7)


RE_SIZES = re.compile(R'\s+(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+0x[0-9a-f]+\s+')


@dataclass
class BarEntry:
    percentage: float
    text: str


def format_bytes(num):
    """
    Human friendly format of byte values.

    :param num: The number to format.
    :return: A string with the formatted number.
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return f'{num:3.1f}'.rstrip('0').rstrip('.') + f' {unit}B'
        num /= 1024.0
    return f'{num:.1f}'.rstrip('0').rstrip('.') + ' YiB'


def print_bar(bar_entries: List[BarEntry]):
    """
    Print a bar with all given entries.

    :param bar_entries: A list of bar entries.
    """
    bar_size = 70
    bar = []
    total = 0.0
    limits = []
    for entry in bar_entries:
        total += entry.percentage
        limits.append(total)
    entry_index = 0
    for char_index in range(bar_size):
        relative_pos = (char_index+1)/bar_size
        if limits[entry_index] > relative_pos:
            bar.append(bar_entries[entry_index].text)
        else:
            entry_index += 1
            if entry_index >= len(limits):
                break
            else:
                bar.append(bar_entries[entry_index].text)
    bar_text = f'{"".join(bar):}'.ljust(bar_size, '.')
    print(f'[{bar_text}] {total*100.0:3.1f}%')


def print_results(text_size: int, initialized_size: int, uninitialized_size: int,
                  flash_size: int, flash_start: int, ram_size: int):
    """
    Print the results of the size command.

    :param text_size: The size of the text segment.
    :param initialized_size: The size of the initialized variables.
    :param uninitialized_size: The size of the uninitialized variables.
    :param flash_size: The total size of the flash rom.
    :param flash_start: The start of the firmware in the flash memory.
    :param ram_size: The size of the RAM in the platform.
    """
    if flash_start > 0:
        print(f'Flash {format_bytes(flash_size)}: {format_bytes(flash_start)} boot / '
              f'{format_bytes(text_size)} code / {format_bytes(initialized_size)} initialized variables')
        bar_entries = [
            BarEntry(percentage=flash_start/flash_size, text='B'),
            BarEntry(percentage=text_size/flash_size, text='C'),
            BarEntry(percentage=initialized_size/flash_size, text='I')
        ]
    else:
        print(f'Flash {format_bytes(flash_size)}: '
              f'{format_bytes(text_size)} code / {format_bytes(initialized_size)} initialized variables')
        bar_entries = [
            BarEntry(percentage=text_size/flash_size, text='C'),
            BarEntry(percentage=initialized_size/flash_size, text='I')
        ]
    print_bar(bar_entries)
    print(f'RAM {format_bytes(ram_size)}: {format_bytes(uninitialized_size)} uninitialized variables / '
          f'{format_bytes(initialized_size)} initialized variables')
    bar_entries = [
        BarEntry(percentage=uninitialized_size/ram_size, text='V'),
        BarEntry(percentage=initialized_size/ram_size, text='I')
    ]
    print_bar(bar_entries)


def retrieve_size(size_tool: str, firmware: str):
    """
    Retrieve the size of the firmware.

    :param size_tool: The absolute path to the size tool.
    :param firmware: The absolute path to the firmware.
    :return: The size of the flash and ram allocation.
    """
    if not Path(size_tool).is_file():
        exit(f'Size tool not found at path: {size_tool}')
    if not Path(firmware).is_file():
        exit(f'Firmware not found at path: {firmware}')
    args = [
        size_tool,
        '-x', '-G',
        firmware
    ]
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        exit(f'The size tool returned an error:\n{result.stdout}')
    match = RE_SIZES.search(result.stdout)
    if not match:
        exit(f'The size tool output could not get parsed:\n{result.stdout}')
    return int(match.group(1), 16), int(match.group(2), 16), int(match.group(3), 16)


def auto_int(argument: str) -> int:
    """
    Convert any int string into an int.

    :param argument: The string with the integer.
    :return: The converted integer.
    """
    return int(argument, 0)


def main():
    """
    Parse the command line arguments.
    """
    parser = argparse.ArgumentParser(description='Visual display the size and allocation of the firmware.')
    parser.add_argument('--flash-size', '-s',
                        dest='flash_size',
                        type=auto_int,
                        action='store',
                        required=True,
                        help='The size of the flash rom of the platform.')
    parser.add_argument('--flash-start', '-b',
                        dest='flash_start',
                        type=auto_int,
                        action='store',
                        required=True,
                        help='The start for the firmware in the flash rom (bootloader).')
    parser.add_argument('--ram-size', '-r',
                        dest='ram_size',
                        type=auto_int,
                        action='store',
                        required=True,
                        help='The size of the RAM of the platform.')
    parser.add_argument('--size-tool', '-t',
                        dest='size_tool',
                        type=str,
                        action='store',
                        required=True,
                        help='The absolute path to the size tool.')
    parser.add_argument('firmware',
                        type=str,
                        action='store',
                        help='The absolute path to the firmware file.')
    args = parser.parse_args()
    text_size, initialized_size, uninitialized_size = retrieve_size(size_tool=args.size_tool, firmware=args.firmware)
    print_results(text_size, initialized_size, uninitialized_size, args.flash_size, args.flash_start, args.ram_size)


if __name__ == '__main__':
    main()
