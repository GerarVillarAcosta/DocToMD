cmake_minimum_required(VERSION 3.15)
project(doctomd_detector C)

set(CMAKE_C_STANDARD 11)

add_executable(detect detect.c)

# Windows: link against kernel32 for GlobalMemoryStatusEx
if(WIN32)
    target_link_libraries(detect PRIVATE kernel32)
    # MSVC runtime static link so the binary runs without redistributables
    if(MSVC)
        set_property(TARGET detect PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
    endif()
endif()

install(TARGETS detect DESTINATION bin)
