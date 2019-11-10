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

# Set the system name
set(CMAKE_SYSTEM_NAME Generic)

# Read the configuration.
if(NOT EXISTS "${CMAKE_CURRENT_LIST_DIR}/configuration.cmake")
    message(FATAL_ERROR "Missing configuration! Please run 'python3 configure.py'...")
endif()
include("${CMAKE_CURRENT_LIST_DIR}/configuration.cmake")

# Additional paths
set(TOOLCHAIN_DIR "${CMAKE_CURRENT_LIST_DIR}")
set(CMSIS_ROOT_PATH "${TOOLCHAIN_DIR}/cmsis/${MCU_NAME}")
set(CMSIS_ATMEL_PATH "${TOOLCHAIN_DIR}/cmsis-atmel")

# Include Paths
set(INCLUDE_PATHS "-I${CMSIS_ROOT_PATH}/include -I${CMSIS_ROOT_PATH}/source -I${CMSIS_ATMEL_PATH}/Include")
set(INCLUDE_PATHS "${INCLUDE_PATHS} -I${TOOLCHAIN_DIR}/platform/${MCU_NAME}")

# Collect flags
set(OPTIMIZATION_FLAGS "-Os")
set(WARNING_FLAGS "-Wall -Wno-unknown-pragmas")
set(CPU_TARGET_FLAGS "-mcpu=${CPU_TARGET} -m${CPU_INST}")
set(MORE_FLAGS "-ffunction-sections -fdata-sections -nostdlib --param max-inline-insns-single=500")
set(CXX_FLAGS "-std=gnu++1z -fno-threadsafe-statics -fno-rtti -fno-exceptions -Wno-register")
set(C_FLAGS "-std=gnu11")

# Set some flags for the C++ compiler.
set(CMAKE_CXX_FLAGS "${CPU_TARGET_FLAGS} ${CXX_FLAGS} ${WARNING_FLAGS} ${OPTIMIZATION_FLAGS} ${MORE_FLAGS}")
set(CMAKE_C_FLAGS "${CPU_TARGET_FLAGS} ${C_FLAGS} ${WARNING_FLAGS} ${OPTIMIZATION_FLAGS} ${MORE_FLAGS}")

# Set the default definitions.
set(d_list F_CPU=48000000L ARM_MATH_CM0PLUS __${MCU_VARIANT}__)
list(TRANSFORM d_list PREPEND "-D")
list(JOIN d_list " " d_flags)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${d_flags}")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${d_flags}")

# Add the default include paths.
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${INCLUDE_PATHS}")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${INCLUDE_PATHS}")

# Set the tools to use.
set(CMAKE_CXX_COMPILER "${APP_TOOLS_PATH}/arm-none-eabi-g++")
set(CMAKE_C_COMPILER "${APP_TOOLS_PATH}/arm-none-eabi-gcc")
set(CMAKE_AR "${APP_TOOLS_PATH}/arm-none-eabi-ar")
set(TOOL_OBJCOPY "${APP_TOOLS_PATH}/arm-none-eabi-objcopy")
set(TOOL_SIZE "${APP_TOOLS_PATH}/arm-none-eabi-size")

# Disable searching the local libraries.
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

set(lf_list
    "${CPU_TARGET_FLAGS}"
    "${C_FLAGS}"
    "${WARNING_FLAGS}"
    "${OPTIMIZATION_FLAGS}"
    "${d_flags}"
    "-T${TOOLCHAIN_DIR}/platform/${TARGET_PLATFORM}/flash_with_bootloader.ld"
    "-Wl,--gc-sections"
    "-Wl,-Map,firmware.map"
    "--specs=nano.specs"
    "--specs=nosys.specs"
    "-Wl,--cref"
    "-Wl,--check-sections"
    "-Wl,--unresolved-symbols=report-all"
    "-Wl,--warn-common"
    "-Wl,--warn-section-align"
    "-Wl,--entry=Reset_Handler"
    "-Wl,--start-group"
#    "-L${CMSIS_ROOT_PATH}/Lib/GCC/ -larm_cortexM0l_math"
    "-lm"
    "-Wl,--end-group"
    "-I${CMSIS_ROOT_PATH}/include"
    "-I${CMSIS_ROOT_PATH}/source"
    "-I${CMSIS_ATMEL_PATH}/Include"
    "-I${TOOLCHAIN_DIR}/platform/${MCU_NAME}")
list(JOIN lf_list " " lf_flags)
set(CMAKE_EXE_LINKER_FLAGS ${lf_flags})

set(CMAKE_CXX_LINK_EXECUTABLE "<CMAKE_C_COMPILER> <LINK_FLAGS> <LINK_LIBRARIES> <OBJECTS> -o <TARGET>")

set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS "")
set(CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS "")
