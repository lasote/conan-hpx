PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

add_definitions(-std=c++14)
ADD_EXECUTABLE(mytest test.cpp)
target_compile_definitions(mytest PUBLIC HPX_APPLICATION_NAME=test HPX_APPLICATION_EXPORTS HPX_ENABLE_ASSERT_HANDLER HPX_HAVE_HWLOC=OFF)
TARGET_LINK_LIBRARIES(mytest ${CONAN_LIBS})
