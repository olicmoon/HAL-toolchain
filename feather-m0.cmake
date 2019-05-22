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

#
# This CMake toolchain will setup the environment to build for a Feather M0 using the Arduino environment.
#
# - The Arduino application version 1.8.9 or later needs to be installed.
# - The Adafruit SAMD toolchain version 1.4.1 or later needs to be installed.
#
# All configurations in this file are made for maxcOS >= 10.14
# It should be possible to port everything to other opertating systems.
#
# Target MCU: SAMD21G18A
#

# Set the system name
set(CMAKE_SYSTEM_NAME Generic)

# The configuration.
set(MCU_NAME "samd21")
set(MCU_VARIANT "SAMD21G18A")
set(CPU_TARGET "cortex-m0plus")
set(CPU_INST "thumb")
set(ADAFRUIT_SAMD_VERSION "1.4.1")
set(ARM_GCC_VERSION "4.8.3-2014q1")
set(CMSIS_VERSION "4.5.0")
set(CMSIS_ATMEL_VERSION "1.2.0")
set(BOSSAC_VERSION "1.7.0")

# The path to the arduino application, which contains the required build encironment.
set(ARDUINO_PATH "/Application/Arduino.app")
set(ARDUINO_JAVA_ROOT "${ARDUINO_PATH}/Contents/Java")
set(ARDUINO_PKG_ROOT "$ENV{HOME}/Library/Arduino15/packages")
set(ARDUINO_TOOLS "${ARDUINO_PKG_ROOT}/arduino/tools")
set(SAMD_BUILD_ROOT "${ARDUINO_PKG_ROOT}/adafruit/hardware/samd/${ADAFRUIT_SAMD_VERSION}")
set(ARDUINO_CORE "${SAMD_BUILD_ROOT}/cores/arduino")
set(APP_TOOLS_PATH "${ARDUINO_TOOLS}/arm-none-eabi-gcc/${ARM_GCC_VERSION}/bin")
set(CMSIS_ROOT_PATH "${ARDUINO_TOOLS}/CMSIS/${CMSIS_VERSION}/CMSIS")
set(CMSIS_ATMEL_ROOT_PATH "${ARDUINO_TOOLS}/CMSIS-Atmel/${CMSIS_ATMEL_VERSION}/CMSIS/Device/ATMEL")
set(VARIANT_ROOT_PATH "${SAMD_BUILD_ROOT}/variants/feather_m0")
set(TOOLCHAIN_DIR "${CMAKE_CURRENT_LIST_DIR}")

# Include Paths
set(INCLUDE_PATHS "-I${ARDUINO_CORE} -I${VARIANT_ROOT_PATH} -I${CMSIS_ROOT_PATH}/Include -I${CMSIS_ATMEL_ROOT_PATH}")
set(INCLUDE_PATHS "${INCLUDE_PATHS} -I${CMSIS_ATMEL_ROOT_PATH}/${MCU_NAME}/include")

# Collect flags
set(OPTIMIZATION_FLAGS "-Os")
set(WARNING_FLAGS "-Wall -Wno-unknown-pragmas")
set(CPU_TARGET_FLAGS "-mcpu=${CPU_TARGET} -m${CPU_INST}")
set(MORE_FLAGS "-ffunction-sections -fdata-sections -nostdlib --param max-inline-insns-single=500")
set(CXX_FLAGS "-std=gnu++11 -fno-threadsafe-statics -fno-rtti -fno-exceptions")
set(C_FLAGS "-std=gnu11")

# Set some flags for the C++ compiler.
set(CMAKE_CXX_FLAGS "${CPU_TARGET_FLAGS} ${CXX_FLAGS} ${WARNING_FLAGS} ${OPTIMIZATION_FLAGS} ${MORE_FLAGS}")
set(CMAKE_C_FLAGS "${CPU_TARGET_FLAGS} ${C_FLAGS} ${WARNING_FLAGS} ${OPTIMIZATION_FLAGS} ${MORE_FLAGS}")

# Set the default definitions.
set(d_list F_CPU=48000000L ARDUINO=10809 ARDUINO_SAMD_ZERO ARDUINO_ARCH_SAMD ARDUINO_SAMD_ZERO ARM_MATH_CM0PLUS
        ADAFRUIT_FEATHER_M0 __${MCU_VARIANT}__ USB_VID=0x239A USB_PID=0x800B USBCON)
list(TRANSFORM d_list PREPEND "-D")
list(APPEND d_list "\"-DUSB_MANUFACTURER=\\\"Adafruit\\\"\"")
list(APPEND s_list "\"-DUSB_PRODUCT=\\\"Feather M0\\\"\"")
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
#set(TOOL_OBJDUMP "${APP_TOOLS_PATH}/arm-none-eabi-objdump")
set(TOOL_OBJCOPY "${APP_TOOLS_PATH}/arm-none-eabi-objcopy")
set(TOOL_SIZE "${APP_TOOLS_PATH}/arm-none-eabi-size")
#set(TOOL_NM "${APP_TOOLS_PATH}/arm-none-eabi-nm")
set(TOOL_BOSSAC "${ARDUINO_TOOLS}/bossac/${BOSSAC_VERSION}/bossac")

# Disable searching the local libraries.
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

set(CMAKE_EXE_LINKER_FLAGS "${CPU_TARGET_FLAGS} ${C_FLAGS} ${WARNING_FLAGS} ${OPTIMIZATION_FLAGS} ${d_flags}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--gc-sections -save-temps")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -T${VARIANT_ROOT_PATH}/linker_scripts/gcc/flash_with_bootloader.ld")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-Map,firmware.map")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} --specs=nano.specs --specs=nosys.specs")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--cref -Wl,--check-sections -Wl,--gc-sections -Wl,--unresolved-symbols=report-all")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--warn-common -Wl,--warn-section-align -Wl,--entry=Reset_Handler")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--start-group")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -L${CMSIS_ROOT_PATH}/Lib/GCC/ -larm_cortexM0l_math")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -L${VARIANT_ROOT_PATH} -lm")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--end-group")

set(CMAKE_CXX_LINK_EXECUTABLE "<CMAKE_C_COMPILER> <LINK_FLAGS> <LINK_LIBRARIES> <OBJECTS> -o <TARGET>")

set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS "")
set(CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS "")
