from conans import ConanFile
from conans.tools import download, unzip, replace_in_file
import os
import shutil
from conans import CMake
from uuid import lib

class HPXConan(ConanFile):
    name = "hpx"
    version = "0.9.11"
    folder = "hpx_%s" % version
    settings = "os", "arch", "compiler", "build_type"
    exports = "CMakeLists.txt"
    generators = "cmake", "txt"
    url="http://github.com/lasote/conan-hpx"
    requires = "Boost/1.59.0@lasote/stable", "hwloc/1.11.1@lasote/stable"

    def config(self):
        # self.options["Boost"].shared = False
        pass
    
    def system_requirements(self):
        if self.settings.os == "Linux": # TODO: only apt
            self.run("sudo apt-get install google-perftools || true")
            # It seems that its not created the symlink properly to normal so and cmake doesnt find it
            # !!!!!!!! we will need the libtcmalloc.so if its linked dynamically, try it
            self.run("sudo ln -s /usr/lib/libtcmalloc.so.4 /usr/lib/libtcmalloc.so || true")
    
    def source(self):
        
        zip_name = "hpx_%s.zip" % self.version
        download("http://stellar.cct.lsu.edu/files/%s" % zip_name, zip_name)
        unzip(zip_name)        

    def build(self):
        """ Define your project building. You decide the way of building it
            to reuse it later in any other project.
        """
        cmakelist_prepend = '''
include(${CMAKE_CURRENT_SOURCE_DIR}/../conanbuildinfo.cmake)
CONAN_BASIC_SETUP()
option(HPX_WITH_EXAMPLES BOOL OFF)
option(HPX_WITH_TESTS BOOL OFF)
'''
        
        replace_in_file("%s/CMakeLists.txt" % self.folder, 'project(HPX CXX C)', 'project(HPX CXX C)\n%s' % cmakelist_prepend)
        # Don't remove module path, keep the previous
        replace_in_file("%s/CMakeLists.txt" % self.folder, 'set(CMAKE_MODULE_PATH', 'set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}')
        # replace_in_file("%s/src/CMakeLists.txt" % self.folder, "if(NOT MSVC)", "if(0)") # Not handle boost Boost_SYSTEM_LIBRARY_DEBUG or Boost_SYSTEM_SERIALIZATION_DEBUG
        
        # Maybe make a PR providing a new option to disable autolink?  link against libraries not directories
        replace_in_file("%s/cmake/HPX_SetupBoost.cmake" % self.folder, "hpx_library_dir(${Boost_LIBRARY_DIRS})", "hpx_libraries(${Boost_LIBRARIES})") # No auto-linking
    
        replace_in_file("%s/src/CMakeLists.txt" % self.folder, "${hpx_MALLOC_LIBRARY}", "${hpx_MALLOC_LIBRARY} ${Boost_SERIALIZATION_LIBRARY}") # Not append boost libs
        
        cmake = CMake(self.settings)
        
        # Build
#         
#         # NO build examples nor tests
#         replace_in_file("%s/CMakeListsOriginal.cmake" % self.folder, "if(HPX_BUILD_EXAMPLES)", "if(FALSE)")
#         replace_in_file("%s/CMakeListsOriginal.cmake" % self.folder, "if(HPX_BUILD_DOCUMENTATION)", "if(FALSE)")
#         replace_in_file("%s/CMakeListsOriginal.cmake" % self.folder, "if(HPX_BUILD_TESTS)", "if(FALSE)")
#         replace_in_file("%s/CMakeListsOriginal.cmake" % self.folder, "if(HPX_BUILD_TOOLS)", "if(FALSE)")
#     
        # CONFIGURE
        self.run("cd %s &&  mkdir _build" % self.folder)
        configure_command = 'cd %s/_build && cmake .. %s ' % (self.folder, cmake.command_line)
        self.output.warn("Configure with: %s" % configure_command)
        self.run(configure_command)
        # BUILD
        cores = "-j3" if self.settings.os != "Windows" else ""
        self.run("cd %s/_build && cmake --build . %s -- %s" % (self.folder, cmake.build_config, cores))

    def package(self):
        """ Define your conan structure: headers, libs and data. After building your
            project, this method is called to create a defined structure:
        """
        self.copy(pattern="*", dst="include/hpx", src="%s/_build/hpx" % self.folder, keep_path=True)
        self.copy(pattern="*", dst="include/", src="%s/external/cache" % self.folder, keep_path=True)
        self.copy(pattern="*", dst="include/", src="%s/external/endian" % self.folder, keep_path=True)
        self.copy(pattern="*", dst="include/hpx", src="%s/hpx" % self.folder, keep_path=True)
        
        self.copy(pattern="*.lib", dst="lib", src="%s/_build" % self.folder, keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="%s/_build" % self.folder, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src="%s/_build" % self.folder, keep_path=False)
        self.copy(pattern="*.so.*", dst="lib", src="%s/_build" % self.folder, keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", src="%s/_build" % self.folder, keep_path=False)
        
        self.copy(pattern="*.dll", dst="bin", src="%s/_build" % self.folder, keep_path=False)
        
        # Copy compilation tools
        self.copy(pattern="*", dst="resources/pkgconfig", src="%s/_build/lib/pkgconfig" % self.folder, keep_path=True)
        self.copy(pattern="*", dst="resources/pkgconfig", src="%s/_build/lib/pkgconfig" % self.folder, keep_path=True)
       
    def package_info(self):  
        # Windows removed (i think examples) => "ag" "cancelable_action" "jacobi_component" "managed_accumulator" and many others
        self.cpp_info.libs = ["hpx", "hpx_init", "hpx_serialization", 
                              "binpacking_factory", "component_storage", "distributing_factory",
                              "iostreams",  "memory", "parcel_coalescing", "remote_object",
                              "unordered", "vector"]
        
	if self.settings.os == "Windows":
            self.cpp_info.libs.extend(["hpx_runtime"])


        if self.settings.build_type == "Debug":
            self.cpp_info.libs = [lib + "d" for lib in self.cpp_info.libs]
            
        
        if self.settings.os == "Linux":
            #self.cpp_info.libs.extend(["pthread","iostreams"])
            pass
        
        if self.settings.compiler != "Visual Studio":
            self.cpp_info.cflags = ["-std=c++11"]
            self.cpp_info.cppflags = ["-std=c++11"]
        
        self.cpp_info.defines.extend(["HPX_COMPONENT_EXPORTS"])
