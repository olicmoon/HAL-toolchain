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
import subprocess
import termios
import time
import argparse
import sys
from pathlib import Path

assert sys.version_info >= (3, 7)


class PortNotFound(Exception):
    """
    Exception if a given port is not found.
    """
    pass


def find_port(port: str) -> str:
    """
    Try to find the specified port.

    In case the user provided wildcard arguments, find the first matching port.

    :param port: The configured port.
    :return: The first port or empty string if no matching port is found.
    """
    if not port or not (port[0].isalnum() or port[0] == '/') or '../' in port or './' in port:
        # Catch some common misuses.
        raise PortNotFound('There was a problem with format of the path to the port.')
    port_path = Path(port)
    if not port_path.is_absolute():
        port_path = Path('/dev')/port_path
    if '*' in port or '?' in port:
        parent_path = port_path.parent
        if '*' in str(parent_path) or '?' in str(parent_path):
            raise PortNotFound('Wildcard characters only allowed in last path element.')
        paths = list(parent_path.glob(port_path.name))
        if not paths:
            raise PortNotFound('No path found matching the specified port pattern.')
        paths.sort()
        port_path = paths[0]
    if not port_path.exists():
        raise PortNotFound('The port path does not exists.')
    if port_path.is_block_device() or port_path.is_char_device():
        return str(port_path)
    else:
        raise PortNotFound('The specified port is no valid block or character device.')


def reset(port: str):
    """
    Open/close the port at 1200 baud will reset the MCU and put it into boot loader mode.
    :param port: The port to use.
    """
    try:
        print('Try to open the port at 1200baud...')
        # Open the port
        fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        # Prepare the configuration.
        iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(fd)
        # Raw / 8N1
        cflag |= (termios.CLOCAL | termios.CREAD | termios.CS8)
        cflag &= ~(termios.CSIZE | termios.CSTOPB)
        lflag &= ~(termios.ICANON | termios.ECHO | termios.ECHOE |
                   termios.ECHOK | termios.ECHONL | termios.ISIG | termios.IEXTEN)
        oflag &= ~(termios.OPOST | termios.ONLCR | termios.OCRNL)
        iflag &= ~(termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IGNBRK | termios.INPCK | termios.ISTRIP)
        # Configure / 1200 baud
        print(f'updating attr {port} {ispeed} {ospeed}')
        custom_baud = termios.B1200
        termios.tcsetattr(fd, termios.TCSANOW, [iflag, oflag, cflag, lflag, custom_baud, custom_baud, cc])
        # Wait
        print('Wait 2 seconds...')
        time.sleep(2)
        print('Close the port and wait 4 seconds for the reset...')
        # Close
        os.close(fd)
        # Wait again.
        time.sleep(4)
    except FileNotFoundError:
        exit(f"Could not find port '{port}'.")
    except termios.error as e:
        exit(f"The path '{port}' is no USB serial line: {e}")


def upload(port: str, firmware: str, tool: str, tool_path: str, flash_start: int):
    """
    Upload the firmware to the platform.

    :param port: The port for the upload.
    :param firmware: The absolute path to the firmware.
    :param tool: The selected tool for the upload.
    :param tool_path: The path to the selected tool.
    :param flash_start: The start address of the firmware in the flash rom.
    """
    print(f'Try to upload the firmware using {tool}...')
    if not tool_path:
        if tool == 'bossac':
            tool_path = 'bossac'
    if not firmware:
        firmware = 'firmware'
    args = [
        tool_path,
        '-o', f'{flash_start:#010x}',
        '-i', f'--port={port}',
        '-R', '-U', '-e', '-w', '-v',
        firmware
    ]
    print(' '.join(args))
    subprocess.run(args)


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
    parser = argparse.ArgumentParser(description='Reset and upload firmware to a platform.')
    parser.add_argument('--port', '-p',
                        dest='port',
                        type=str,
                        action='store',
                        default='/dev/cu.usbmodem*',
                        help='The USB port to reset as absolute path to the device. E.g.: /dev/cu.usbmodemXXXX).' +
                        'Can contain wildcards to select the first matching device.')
    parser.add_argument('--reset', '-r',
                        dest='reset',
                        action='store_true',
                        help='If set, the port is set to 1200baud to reset the platform.')
    parser.add_argument('--upload', '-u',
                        dest='upload',
                        action='store_true',
                        help='If set the firmware is uploaded.')
    parser.add_argument('--firmware', '-f',
                        dest='firmware',
                        type=str,
                        action='store',
                        help='The path to the firmware.')
    parser.add_argument('--tool', '-t',
                        dest='tool',
                        type=str,
                        action='store',
                        default='bossac',
                        choices=['bossac'],
                        help='The tool to use.')
    parser.add_argument('--tool-path', '-x',
                        dest='tool_path',
                        type=str,
                        action='store',
                        help='The absolute path to the used tool.')
    parser.add_argument('--flash-start', '-b',
                        dest='flash_start',
                        type=auto_int,
                        action='store',
                        default=0x2000,
                        help='The base address of the firmware.')

    args = parser.parse_args()
    if not (args.reset or args.upload):
        print('Please specify upload (-u) or reset (-r) or both.')
        parser.print_help()
        exit(1)
    try:
        port = find_port(args.port)
    except PortNotFound as e:
        exit(f'Port "{args.port}" not found: {e}')
        return
    if args.reset:
        reset(port=port)
    if args.upload:
        upload(port=port,
               firmware=args.firmware,
               tool=args.tool,
               tool_path=args.tool_path,
               flash_start=args.flash_start)


if __name__ == '__main__':
    main()
