# Set the minimum required version of CMake
cmake_minimum_required(VERSION 3.14)

# Set the project name
project(arduino-core)

# Create symlinks for all required source files.
set(arduino_core_dir "${CMAKE_CURRENT_LIST_DIR}/arduino_core")
set(cmsis_atmel_dir "${CMAKE_CURRENT_LIST_DIR}/cmsis_atmel")
set(arduino_variant_dir "${CMAKE_CURRENT_LIST_DIR}/arduino_variant")
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

# Create a static library from all this f
add_library(arduino-core STATIC ${ARDUINO_CORE_FILES})


