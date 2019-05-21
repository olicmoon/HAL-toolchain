# Set the minimum required version of CMake
cmake_minimum_required(VERSION 3.14)

# Set the project name
project(arduino-core)


# Function to add targets for the firmware.
function(arduino_link TARGET)
    set(FIRMWARE_TARGET firmware)
    add_executable(${FIRMWARE_TARGET} "${TOOLCHAIN_DIR}/arduino-link/empty.c")
    target_link_libraries(${FIRMWARE_TARGET} arduino-core ${TARGET})

    add_custom_command(TARGET ${FIRMWARE_TARGET} POST_BUILD COMMAND "${TOOL_OBJCOPY}" ARGS "-O" "binary"
            "$<TARGET_FILE_NAME:${FIRMWARE_TARGET}>" "$<TARGET_FILE_NAME:${FIRMWARE_TARGET}>.bin"
            WORKING_DIRECTORY "$<TARGET_FILE_DIR:${FIRMWARE_TARGET}>")
    add_custom_command(TARGET ${FIRMWARE_TARGET} POST_BUILD COMMAND "${TOOL_SIZE}" ARGS "-A"
            "$<TARGET_FILE_NAME:${FIRMWARE_TARGET}>"
            WORKING_DIRECTORY "$<TARGET_FILE_DIR:${FIRMWARE_TARGET}>")
endfunction()
