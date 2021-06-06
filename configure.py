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

import re
import subprocess
import argparse
import sys
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path
from typing import Dict, Optional

assert sys.version_info >= (3, 7)


TARGET_PLATFORM = 'feather-m0'
TARGET_MCU = 'samd21'
TARGET_MCU_VARIANT = 'SAMD21G18A'
TARGET_CPU_TYPE = 'cortex-m0plus'
TARGET_CPU_INSTRUCTIONS = 'thumb'
CONFIG_FILE = 'configuration.cmake'
FLASH_SIZE = 0x00040000
FLASH_START = 0x00002000
RAM_SIZE = 0x00008000

BIN_DIRS = [Path('/usr/bin'), Path('/usr/local/bin')]
COMPILER_NAME = 'arm-none-eabi-gcc'
BOSSAC_NAME = 'bossac'
PYTHON3_PATH = sys.executable


class Error(Exception):
    """The error class for this script."""


@total_ordering
class Version:
    """A class to handle version numbers"""

    def __init__(self, text: str):
        self.parts = text.lower().split('.')

    def __eq__(self, other):
        return self.parts == other.parts

    def __lt__(self, other):
        return self.parts < other.parts

    def __str__(self):
        return '.'.join(self.parts)


@dataclass
class Configuration:
    """The configuration created for the system."""
    verbose: bool = False
    compiler_path: Optional[Path] = None
    bossac_path: Optional[Path] = None


COMPILER_MIN_VERSION = Version('6.3.1')
BOSSAC_MIN_VERSION = Version('1.9.0')


config = Configuration()  # The configuration used for this tool.


def scan_compiler():
    """
    Scan for the compiler.
    """
    compiler_path = config.compiler_path
    if not compiler_path:
        for bin_dir in BIN_DIRS:
            if (bin_dir/COMPILER_NAME).is_file():
                compiler_path = bin_dir
    if not compiler_path:
        raise Error('Could not find the ARM compiler in your path. Please specify the compiler directory using '
                    'the -c command line argument.')
    compiler_bin = compiler_path/COMPILER_NAME
    args = [str(compiler_bin), '--version']
    if config.verbose:
        print(f'Checking compiler version: {" ".join(args)}')
    try:
        result = subprocess.run(args, capture_output=True)
    except subprocess.SubprocessError:
        raise Error(f'Could not start compiler command at: {str(compiler_bin)}')
    if not result:
        raise Error(f'Could not start compiler command at: {str(compiler_bin)}')
    if result.returncode != 0:
        if config.verbose:
            print(f'Output: {result.stdout.decode("utf-8")}')
        raise Error(f'Compiler version check returned non-zero: {str(compiler_bin)}')
    re_version = re.compile(R'\s+(\d+\.\d+\.\d+)\s+')
    match = re_version.search(result.stdout.decode('utf-8'))
    if not match:
        raise Error(f'Could not detect the ARM compiler version.')
    compiler_version = Version(match.group(1))
    if compiler_version < COMPILER_MIN_VERSION:
        raise Error(f'Found compiler version {compiler_version}, but minimum version '
                    f'{COMPILER_MIN_VERSION} is required.')
    config.compiler_path = compiler_path/'bin'
    if config.verbose:
        print(f'Found compiler version {compiler_version} here: {config.compiler_path}')


def scan_bossac():
    """
    Search for the bossac tool.
    """
    bossac_path = config.bossac_path
    if not bossac_path:
        for bin_dir in BIN_DIRS:
            if (bin_dir/BOSSAC_NAME).is_file():
                bossac_path = bin_dir/BOSSAC_NAME
    if not bossac_path:
        raise Error('Could not find the "bossac" tool in the regular binary paths. Please specify the '
                    'path to the tool using the -b command line argument.')
    args = [str(bossac_path), '-h']
    if config.verbose:
        print(f'Checking bossac version: {" ".join(args)}')
    try:
        result = subprocess.run(args, capture_output=True)
    except subprocess.SubprocessError:
        raise Error(f'Could not start bossac command at: {str(bossac_path)}')
    if not result:
        raise Error(f'Could not start bossac command at: {str(bossac_path)}')
    re_version = re.compile(R'\s+(\d+\.\d+\.\d+)\s+')
    match = re_version.search(result.stdout.decode('utf-8'))
    if not match:
        if config.verbose:
            print(f'Output: {result.stdout.decode("utf-8")}')
        raise Error(f'Could not detect the bossac version.')
    bossac_version = Version(match.group(1))
    if bossac_version < BOSSAC_MIN_VERSION:
        raise Error(f'Found bossac version {bossac_version}, but minimum version '
                    f'{BOSSAC_MIN_VERSION} is required.')
    config.bossac_path = bossac_path
    if config.verbose:
        print(f'Found bossac version {bossac_version} here: {config.bossac_path}')


def scan_system():
    """
    Scan the system for required directories.
    """
    scan_compiler()
    scan_bossac()


def write_config():
    """
    Write the final configuration.
    """
    if config.verbose:
        print('Preparing configuration...')
    variables = {
        'MCU_NAME': TARGET_MCU.lower(),
        'MCU_VARIANT': TARGET_MCU_VARIANT.upper(),
        'TARGET_PLATFORM': TARGET_PLATFORM.lower(),
        'CPU_TARGET': TARGET_CPU_TYPE.lower(),
        'CPU_INST': TARGET_CPU_INSTRUCTIONS.lower(),
        'APP_TOOLS_PATH': str(config.compiler_path),
        'BOSSAC_PATH': str(config.bossac_path),
        'PYTHON3_PATH': str(PYTHON3_PATH),
        'FLASH_SIZE': f'{FLASH_SIZE:#010x}',
        'FLASH_START': f'{FLASH_START:#010x}',
        'RAM_SIZE': f'{RAM_SIZE:#010x}',
    }
    if config.verbose:
        print(' - Configuration:')
        for key, value in variables.items():
            print(f'   {key}: {value}')
    lines = [
        '#',
        '# Do not modify this file! It was generated by the "configure.py" script.',
        '#',
        ''
    ]
    for key, value in variables.items():
        lines.append(f'set({key} "{value}")')
    lines.extend(['', '', ''])
    config_path = Path(__file__).parent / CONFIG_FILE
    print(f'Writing configuration: {config_path}')
    config_path.write_text('\n'.join(lines), 'utf-8')


def main():
    """
    Parse the command line arguments and reset the line.
    """
    parser = argparse.ArgumentParser(
        description='This script scans your system for required paths to compile firmware using the HAL system.')
    parser.add_argument('-v', '--verbose',
                        required=False,
                        action='store_true',
                        dest='verbose',
                        help='Enable verbose messages.')
    parser.add_argument('-c', '--compiler',
                        required=False,
                        action='store',
                        dest='compiler_path',
                        help='Use this command line option to specify the path to the ARM compiler on your '
                             'system.')
    parser.add_argument('-b', '--bossac',
                        required=False,
                        action='store',
                        dest='bossac_path',
                        help='Set the path to the BOSSAc executable manually if it can not be detected.')
    args = parser.parse_args()
    if args.verbose:
        config.verbose = True
    if args.compiler_path:
        config.compiler_path = Path(args.compiler_path)
    if args.bossac_path:
        config.bossac_path = Path(args.bossac_path)
    try:
        scan_system()
        write_config()
        print('SUCCESS!')
        exit(0)
    except Error as error:
        exit(f'ERROR! {error}')


if __name__ == '__main__':
    main()
