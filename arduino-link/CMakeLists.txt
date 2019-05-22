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

# Function to add targets for the firmware.
function(arduino_link TARGET)
    # Check some variables
    if (NOT DEFINED UPLOAD_PORT)
        message(FATAL_ERROR "You have to define UPLOAD_PORT in your main CMakeLists.txt file.")
    endif()
    if (NOT TARGET ${TARGET})
        message(FATAL_ERROR "The parameter of 'arduino_link' has to be a valid target.")
    endif()
    # Add an additional target to link a final executable with the core libraries.
    set(FIRMWARE_TARGET firmware)
    add_executable(${FIRMWARE_TARGET} "${TOOLCHAIN_DIR}/arduino-link/empty.c")
    target_link_libraries(${FIRMWARE_TARGET} arduino-core ${TARGET})
    # Add additional custom commands to convert the linked file into a binary file.
    add_custom_command(TARGET ${FIRMWARE_TARGET} POST_BUILD COMMAND "${TOOL_OBJCOPY}" ARGS "-O" "binary"
            "$<TARGET_FILE_NAME:${FIRMWARE_TARGET}>" "$<TARGET_FILE_NAME:${FIRMWARE_TARGET}>.bin"
            WORKING_DIRECTORY "$<TARGET_FILE_DIR:${FIRMWARE_TARGET}>")
    add_custom_command(TARGET ${FIRMWARE_TARGET} POST_BUILD COMMAND "${TOOL_SIZE}" ARGS "-A"
            "$<TARGET_FILE_NAME:${FIRMWARE_TARGET}>"
            WORKING_DIRECTORY "$<TARGET_FILE_DIR:${FIRMWARE_TARGET}>")
    # Add the intsllation script to upload the firmware.
    install(CODE "execute_process(COMMAND
        ${CMAKE_COMMAND}
        \"-DUPLOAD_PORT=${UPLOAD_PORT}\"
        \"-DFIRMWARE=$<TARGET_FILE:${FIRMWARE_TARGET}>.bin\"
        \"-DBOSSAC=${TOOL_BOSSAC}\"
        -P \"${TOOLCHAIN_DIR}/arduino-link/upload.cmake\")")
endfunction()

