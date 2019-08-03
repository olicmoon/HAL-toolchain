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

# Set the minimum required version of CMake
cmake_minimum_required(VERSION 3.14)

# Set the project name
project(arduino-core)

# Create symlinks for all required source files.
set(core_files_dir "${CMAKE_CURRENT_LIST_DIR}/dependencies/${CMAKE_BUILD_TYPE}")
set(arduino_core_dir "${core_files_dir}/arduino_core")
set(cmsis_atmel_dir "${core_files_dir}/cmsis_atmel")
set(arduino_variant_dir "${core_files_dir}/arduino_variant")
if(NOT EXISTS "${arduino_core_dir}")
    execute_process(COMMAND "mkdir" "-p" "${core_files_dir}")
endif()
execute_process(COMMAND "rm" "-f" "${arduino_core_dir}" "${cmsis_atmel_dir}" "${arduino_variant_dir}")
execute_process(COMMAND "ln" "-s" "${ARDUINO_CORE}" "${arduino_core_dir}")
execute_process(COMMAND "ln" "-s" "${CMSIS_ATMEL_ROOT_PATH}/${MCU_NAME}" "${cmsis_atmel_dir}")
execute_process(COMMAND "ln" "-s" "${VARIANT_ROOT_PATH}" "${arduino_variant_dir}")

# Scan for all files.
file(GLOB_RECURSE ARDUINO_CORE_FILES
        "${arduino_core_dir}/*.cpp"
        "${arduino_core_dir}/*.c"
        "${cmsis_atmel_dir}/source/*.c"
        "${arduino_variant_dir}/*.cpp")

# Create a static library from all this files.
add_library(arduino-core STATIC ${ARDUINO_CORE_FILES})

# Supress warnings of the core files.
set_target_properties(arduino-core PROPERTIES COMPILE_FLAGS "-Wno-unused-variable")
