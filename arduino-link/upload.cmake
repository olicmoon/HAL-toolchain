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

# Check if we got all required variables.
if (NOT DEFINED FIRMWARE)
    message(FATAL_ERROR "The variable FIRMWARE is not defined.")
endif()
if (NOT DEFINED UPLOAD_PORT)
    message(FATAL_ERROR "The variable UPLOAD_PORT is not defined.")
endif()
if (NOT DEFINED BOSSAC)
    message(FATAL_ERROR "The variable BOSSAC is not defined.")
endif()

# Reset the board.
message("Try to reset the board...")
execute_process(
        COMMAND "python3"
        "${CMAKE_CURRENT_LIST_DIR}/port_reset.py" "--port=${UPLOAD_PORT}"
        OUTPUT_VARIABLE reset_output
        ERROR_VARIABLE reset_output)
message("${reset_output}")

# Upload the new firmware.
message("Start upload...")
execute_process(
        COMMAND "${BOSSAC}"
        "-i" "--port=${UPLOAD_PORT}" "-U" "true" "-R"  "-e" "-w" "-v" "${FIRMWARE}"
        OUTPUT_VARIABLE uploader_output
        ERROR_VARIABLE uploader_output)
message("${uploader_output}")

