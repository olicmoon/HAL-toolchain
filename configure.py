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

import enum
import os
import re
import subprocess
import argparse
import sys
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path
from typing import Dict, Optional

assert sys.version_info >= (3, 7)


class OperatingSystem(enum.Enum):
    """The operating system."""
    MAC_OS = 1
    LINUX = 2


ARDUINO_LOCATIONS: Dict[Path, OperatingSystem] = {
    Path('/Applications/Arduino.app'): OperatingSystem.MAC_OS,
    (Path.home() / 'Applications/Arduino.app'): OperatingSystem.MAC_OS,
    (Path.home() / '.arduino15'): OperatingSystem.LINUX,
}

TARGET_PLATFORM = 'Feather M0'
TARGET_MCU = 'samd21'
TARGET_MCU_VARIANT = 'SAMD21G18A'
TARGET_CPU_TYPE = 'cortex-m0plus'
TARGET_CPU_INSTRUCTIONS = 'thumb'
CONFIG_FILE = 'feather-m0-config.cmake'


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
class BuildPath:
    """The configuration for a single build path."""
    name: str  # The name of the package.
    cmake_name: str  # The CMake variable name
    package_path: Path  # The relative path to the package
    minimum_version: Version  # The minimum version for the path.
    maximum_version: Version = None  # The maximum version for the path.
    path_suffix: Path = None  # Suffix to add to the path after the version.


BUILD_PATHS = [
    BuildPath(
        name='Adafruit SAMD Boards',
        cmake_name='SAMD_BUILD_ROOT',
        minimum_version=Version('1.5.2'),
        package_path=Path('adafruit/hardware/samd')),
    BuildPath(
        name='ARM GCC Compiler',
        cmake_name='APP_TOOLS_PATH',
        minimum_version=Version('4.8.3-2014q1'),
        package_path=Path('arduino/tools/arm-none-eabi-gcc'),
        path_suffix=Path('bin')
    ),
    BuildPath(
        name='CMSIS',
        cmake_name='CMSIS_ROOT_PATH',
        minimum_version=Version('4.5.0'),
        package_path=Path('arduino/tools/CMSIS'),
        path_suffix=Path('CMSIS')
    ),
    BuildPath(
        name='Atmel CMSIS',
        cmake_name='CMSIS_ATMEL_ROOT_PATH',
        minimum_version=Version('1.2.0'),
        package_path=Path('arduino/tools/CMSIS-Atmel'),
        path_suffix=Path('CMSIS/Device/ATMEL')
    ),
    BuildPath(
        name='Bossac Uploader',
        cmake_name='TOOL_BOSSAC',
        minimum_version=Version('1.7.0'),
        maximum_version=Version('1.7.0'),
        package_path=Path('arduino/tools/bossac'),
        path_suffix=Path('bossac')
    )
]

ARDUINO_MINIMUM_VERSION = Version('1.8.9')


@dataclass
class Configuration:
    """The configuration created for the system."""
    verbose: bool = False
    operating_system: OperatingSystem = None
    arduino_bin_path: Path = None
    arduino_version: Version = None
    arduino_java_path: Path = None
    arduino_package_root: Path = None
    build_paths: Dict[str, Path] = None


config = Configuration()  # The configuration used for this tool.


def get_macos_version(path: Path) -> (Version, Path):
    """For macOS we found the actual Arduino application"""
    config.arduino_bin_path = path
    info_file = path / 'Contents' / 'info.plist'
    if not info_file.is_file():
        raise Error('Could not read the version from the Arduino application. '
                    f'File not found: {info_file.as_posix()}')
    info_content = info_file.read_text('utf-8')
    match = re.search(r'<key>CFBundleShortVersionString</key>\s*<string>([^<]+)</string>', info_content, re.I)
    if not match:
        raise Error('Could not read the version from the Arduino application. '
                    f'The failed file was: {info_file.as_posix()}')
    return Version(match.group(1)), (path / 'Contents' / 'Java')


def get_linux_version() -> (Version, Path):
    """For linux we just find the library directory."""
    if config.verbose:
        print(' - Searching for arduino executable...')
    if not config.arduino_bin_path:
        if config.verbose:
            print('   - Check if there is a desktop entry...')
        for link_path in (Path.home() / 'Desktop').glob('*.desktop'):
            if 'arduino' in link_path.as_posix().lower():
                if config.verbose:
                    print(f'   - Found: {str(link_path)}')
                link_content = link_path.read_text('utf-8')
                match = re.search(r'\nExec\s*=\s*(.*)\s*\n', link_content, re.I)
                if not match:
                    raise Error('Found desktop entry, but missing the "Exec" line in this file. '
                                f'Checked file: {link_path.as_posix()}')
                path = match.group(1)
                if config.verbose:
                    print(f'   - Includes path: "{path}"')
                config.arduino_bin_path = Path(path)
                break
    if config.arduino_bin_path and config.verbose:
        print(f'   - Found arduino executable at: {str(config.arduino_bin_path)}')
    if not config.arduino_bin_path and not config.arduino_bin_path.is_file():
        raise Error('The found arduino binary path is no file. '
                    f'Found path: {config.arduino_bin_path}')
    # Retrieve the version
    args = [
        config.arduino_bin_path,
        '--version'
    ]
    if config.verbose:
        print(' - Starting the Arduino executable to get the version.')
    result = subprocess.run(args, capture_output=True)
    output = result.stdout.decode('utf-8')
    match = re.search(r'Arduino:\s*([.0-9a-z]+)\s*\n', output, re.I)
    if not match:
        raise Error('Got an unexpected result from the executable.')
    version = match.group(1)
    return Version(version), config.arduino_bin_path.parent


def get_arduino_version(path: Path, operating_system: OperatingSystem) -> (Version, Path):
    """
    Detect the arduino version at the given path and for the given operating system.
    :param path: The path where it is installed.
    :param operating_system: The operating system for the given path.
    :return: The version and the path to the java directory.
    """
    if operating_system == OperatingSystem.MAC_OS:
        return get_macos_version(path)
    elif operating_system == OperatingSystem.LINUX:
        return get_linux_version()


def scan_system():
    """
    Scan the system for required directories.
    """
    # Check the operating system.
    if os.name == 'nt':
        raise Error('Windows is not supported. This toolchain only works with macOS and Linux or similar.')
    # Find the Arduino IDE on the system.
    if config.verbose:
        print('Scanning for Arduino environment...')
    for path, operating_system in ARDUINO_LOCATIONS.items():
        if config.verbose:
            print(f' - Scanning path {path.as_posix()}')
        if path.is_dir():
            if config.verbose:
                print(f'   - Found directory. Checking version.')
            version, java_path = get_arduino_version(path, operating_system)
            if version < ARDUINO_MINIMUM_VERSION:
                raise Error(f'Found Arduino version {version} but requires version {ARDUINO_MINIMUM_VERSION}. '
                            f'Checked the IDE at the following path: {path.as_posix()}')
            config.operating_system = operating_system
            config.arduino_version = version
            config.arduino_java_path = java_path
            break
    if not config.operating_system:
        raise Error('Could not find an installed arduino environment.')
    print(f'Found Arduino {config.arduino_version} at path: {config.arduino_java_path}')
    # Find the package root directory.
    if config.operating_system == OperatingSystem.MAC_OS:
        config.arduino_package_root = Path.home() / 'Library' / 'Arduino15' / 'packages'
    elif config.operating_system == OperatingSystem.LINUX:
        config.arduino_package_root = Path.home() / '.arduino15' / 'packages'
    print(f'Using package directory: {config.arduino_package_root}')


def find_latest_package(root_path: Path, name: str,
                        minimum_version: Version,
                        maximum_version: Optional[Version]) -> Version:
    """
    Get the latest version of a package.
    :param root_path: The root path to scan for versions.
    :param name: The name of the package.
    :param minimum_version: The minimum version.
    :return: The latest found version.
    """
    if config.verbose:
        print(f' - Check the "{name}" package version.')
    if not root_path.is_dir():
        raise Error(f'Please install the "{name}" package".')
    versions = []
    for path in root_path.glob('*'):
        if path.name == '.' or path.name == '..' or not path.is_dir():
            continue
        versions.append(Version(path.name))
    versions.sort()
    if not versions:
        raise Error(f'Please install the "{name}" package".')
    if config.verbose:
        version_strings = [str(v) for v in versions]
        print(f'   - Found these versions: {", ".join(version_strings)}')
    for test_version in reversed(versions):
        if maximum_version and test_version > maximum_version:
            if config.verbose:
                print(f'   - Ignoring version {test_version}, because it is over maximum version {maximum_version}')
            continue
        if test_version < minimum_version:
            raise Error(f'Installed "{name}" package needs to be updated. '
                        f'found version {test_version}, but requires {minimum_version}.')
        version = test_version
        break
    if not version:
        raise Error(f'Found no matching version for package "{name}". '
                    f'Minimum version {minimum_version} and maximum {maximum_version if maximum_version else "-"}')
    if config.verbose:
        print(f'   - Use version: {version}')
    return version


def find_package_versions():
    """
    Check if the required packages are installed on the system.
    """
    build_paths = {}
    for build_path in BUILD_PATHS:
        root_path = config.arduino_package_root / build_path.package_path
        version = find_latest_package(root_path, build_path.name,
                                      build_path.minimum_version, build_path.maximum_version)
        final_path = root_path / str(version)
        if build_path.path_suffix:
            final_path = final_path / build_path.path_suffix
        build_paths[build_path.cmake_name] = final_path
    config.build_paths = build_paths
    if config.verbose:
        print("Check if all paths exist...")
    for key, value in build_paths.items():
        if not value.exists():
            raise Error(f'Required path {key} not found: {value}')


def write_config():
    """
    Write the final configuration.
    """
    if config.verbose:
        print('Preparing configuration...')
    variables = {
        'MCU_NAME': TARGET_MCU.lower(),
        'MCU_VARIANT': TARGET_MCU_VARIANT.upper(),
        'CPU_TARGET': TARGET_CPU_TYPE.lower(),
        'CPU_INST': TARGET_CPU_INSTRUCTIONS.lower(),
        'ARDUINO_JAVA_ROOT': config.arduino_java_path.as_posix(),
    }
    if config.verbose:
        print(' - Configuration:')
        for key, value in variables.items():
            print(f'   {key}: {value}')
        print(' - Paths:')
    for build_path in BUILD_PATHS:
        name = build_path.cmake_name
        value = str(config.build_paths[name])
        if config.verbose:
            print(f'   {name}: {value}')
        variables[name] = value
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
    parser = argparse.ArgumentParser(description='Configure the Toolchain')
    parser.add_argument('-v', '--verbose',
                        required=False,
                        action='store_true',
                        dest='verbose',
                        help='Enable verbose messages.')
    parser.add_argument('-a', '--arduino',
                        required=False,
                        action='store',
                        dest='arduino_path',
                        help='Set the path to the arduino executable manually if it can not be detected.')
    args = parser.parse_args()
    if args.verbose:
        config.verbose = True
    if args.arduino_path:
        config.arduino_bin_path = Path(args.arduino_path)
    try:
        scan_system()
        find_package_versions()
        write_config()
        print('SUCCESS!')
        exit(0)
    except Error as error:
        exit(f'ERROR! {error}')


if __name__ == '__main__':
    main()
