HAL-toolchain
=============

This directory contains a CMake toolchain to build and upload a firmware using the HAL system for a board.

Adafruit Feather M0
-------------------
Make sure you have all prerequisites:

- Install the Arduino IDE, version 1.8.9 or later.
- Install the "Adafruit SAMD Boards" package.
- Install the "Arduino SAMD Boards" package.
- Install CMake version 3.14 or later.
- Install Python version 3.7 or later.

Prepare a project for using the configuration script

- Run `python3 configure.py` to create the `feather-m0-config.cmake` file. The script will scan your system for correct paths used for the toolchain.
- Update the `UPLOAD_PORT` in the `CMakeLists.txt` of the project root directory.

Create the build environment:

- Create a new empty directory: `mkdir ~/blink-build`
- Change into this directory: `cd ~/blink-build`
- Run `cmake` using the toolchain. Assuming `~/hal-example-fm0-blink` is the directory of the project and `~/blink-build` is the build directory.

```
mkdir ~/blink-build
cd ~/blink-build
cmake -DCMAKE_TOOLCHAIN_FILE=~/hal-example-fm0-blink/hal-toolchain/feather-m0.cmake
```

Build the Firmware
------------------
To build the firmware, just run `make` from the build directory:

```
cd ~/blink-build
make
```

Upload the Firmware
-------------------
To upload the firmware, just run `make install`:

```
cd ~/blink-build
make install
```

Examples
--------
See the `hal-example-fm0-blink` for a working example project:

https://github.com/LuckyResistor/HAL-example-fm0-blink

Notes About IDE Usage
---------------------
This toolchain creates symlinks in the `arduino-core` library to the correct source directories. These directories are created to make editing of projects simpler for IDEs like CLion.

By adding these symlinks, all required files are added at a defined place in the source tree. Without the symlinks, some IDEs (like CLion) will add all files to the project root, which is inconvenient.

Status
------
This library is a work in progress. It is published merely as an inspiration and in the hope it may be useful. 

License
-------
Copyright 2019 by Lucky Resistor.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

