#!/usr/bin/python3
#
# HAL Toolchain
# ---------------------------------------------------------------------------
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
import termios
import time
import argparse
import sys

assert sys.version_info >= (3, 7)


def reset(port: str):
    """
    Open/close the port at 1200 baud will reset the MCU and put it into boot loader mode.
    :param port: The port to use.
    """
    try:
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
        termios.tcsetattr(fd, termios.TCSANOW, [iflag, oflag, cflag, lflag, 1200, 1200, cc])
        # Wait
        time.sleep(2)
        # Close
        os.close(fd)
        # Wait again.
        time.sleep(3)
    except FileNotFoundError:
        exit(f"Could not find port '{port}'.")
    except termios.error:
        exit(f"The path '{port}' is no USB serial line.")


def main():
    """
    Parse the command line arguments and reset the line.
    """
    parser = argparse.ArgumentParser(description='Reset Platform into Bootloader')
    parser.add_argument('--port', '-p',
                        dest='port',
                        type=str,
                        action='store',
                        required=True,
                        help='The USB port to reset (like /dev/cu.usbmodemXXXX)')
    args = parser.parse_args()
    reset(args.port)


if __name__ == '__main__':
    main()
