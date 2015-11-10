from conans import ConanFile
from conans.tools import download, unzip
import os
import shutil
from conans import CMake
from uuid import lib

class HPXConan(ConanFile):
    name = "hpx"
    version = "0.9.10"
    folder = "hpx_%s" % version
    settings = "os", "arch", "compiler", "build_type"
    exports = "CMakeLists.txt"
    generators = "cmake", "txt"
    url="http://github.com/lasote/conan-hpx"
    requires = "Boost/1.57.0@lasote/stable", "hwloc/1.11.1@lasote/stable"

    def config(self):
        pass
    
    def system_requirements(self):
        if self.settings.os == "Linux": # TODO: only apt
            self.run("sudo apt-get install google-perftools || true")
            # It seems that its not created the symlink properly to normal so and cmake doesnt find it
            self.run("sudo ln -s /usr/lib/libtcmalloc.so.4 /usr/lib/libtcmalloc.so || true")
    
    def source(self):
        
        zip_name = "hpx_%s.zip" % self.version
        download("http://stellar.cct.lsu.edu/files/%s" % zip_name, zip_name)
        unzip(zip_name)
        shutil.move("%s/CMakeLists.txt" % self.folder, "%s/CMakeListsOriginal.cmake" % self.folder)
        shutil.move("CMakeLists.txt", "%s/CMakeLists.txt" % self.folder)

    def build(self):
        """ Define your project building. You decide the way of building it
            to reuse it later in any other project.
        """
        cmake = CMake(self.settings)
        # Get boost serialization library name
        serialization_lib_name = ""
        for lib in self.deps_cpp_info.libs:
            if "serialization" in lib: # From Boost dependency
                serialization_lib_name = lib
                break
        
        
        # Build
        
        #Hacks for link with out boost and hwloc
        boost_version = "SET(Boost_VERSION 105700)"
        boost_found = "SET(Boost_FOUND TRUE)"
        boost_libraries = "SET(Boost_LIBRARIES %s)" % " ".join(self.deps_cpp_info.libs)
        boost_include_dir = "SET(Boost_INCLUDE_DIR %s)" % self.get_include_dir("Boost")
        replace_line = "\n%s\n%s\n%s\n%s\n\n" % (boost_version, boost_found, boost_libraries, boost_include_dir)
        
        self.replace_in_file("%s/cmake/HPX_SetupBoost.cmake" % self.folder, "find_package(Boost", "SET(DONTWANTTOFINDBOOST") # Not find boost, i have it
        self.replace_in_file("%s/cmake/HPX_SetupBoost.cmake" % self.folder, "if(NOT Boost_FOUND)", "%sif(NOT Boost_FOUND)" % replace_line) # Not find boost, i have it
        
        
        hwloc_found = "SET(HWLOC_FOUND TRUE)"
        hwloc_libraries = "SET(HWLOC_LIBRARIES %s)" % " ".join(self.deps_cpp_info.libs)
        hwloc_include_dir = "SET(HWLOC_INCLUDE_DIR %s)" % self.get_include_dir("hwloc")
        replace_line = "\n%s\n%s\n%s\n\n" % (hwloc_found, hwloc_libraries, hwloc_include_dir)
        
        self.replace_in_file("%s/CMakeListsOriginal.cmake" % self.folder, "find_package(Hwloc)", 'MESSAGE("hwloc found by conan")\n%s' % replace_line) # Not find hwloc, i have it
        
        # OTHER REPLACES
        self.replace_in_file("%s/src/CMakeLists.txt" % self.folder, "if(NOT MSVC)", "if(0)") # Not handle boost Boost_SYSTEM_LIBRARY_DEBUG or Boost_SYSTEM_SERIALIZATION_DEBUG
        self.replace_in_file("%s/src/CMakeLists.txt" % self.folder, "${hpx_MALLOC_LIBRARY}", "${hpx_MALLOC_LIBRARY} %s" % serialization_lib_name) # Not append boost libs
        
        
        # CONFIGURE
        self.run("cd %s &&  mkdir _build" % self.folder)
        configure_command = 'cd %s/_build && cmake .. %s ' % (self.folder, cmake.command_line)
        self.output.warn("Configure with: %s" % configure_command)
        self.run(configure_command)
        # BUILD
        cores = "-j3" if self.settings.os == "Linux" else "-m4"
        self.run("cd %s/_build && cmake --build . %s -- %s" % (self.folder, cmake.build_config, cores))

    def replace_in_file(self, file_path, search, replace):
        with open(file_path, 'r') as content_file:
            content = content_file.read()
            content = content.replace(search, replace)
        with open(file_path, 'wb') as handle:
            handle.write(content)
            
    def get_include_dir(self, require_name):
        for thedir in self.deps_cpp_info.includedirs:
            if require_name in thedir:
                return thedir
        return "" 

    def package(self):
        """ Define your conan structure: headers, libs and data. After building your
            project, this method is called to create a defined structure:
        """
        self.copy(pattern="*", dst="include/hpx", src="%s/_build/hpx" % self.folder, keep_path=True)
        self.copy(pattern="*", dst="include/", src="%s/external/cache" % self.folder, keep_path=True)
        self.copy(pattern="*", dst="include/", src="%s/external/endian" % self.folder, keep_path=True)
        self.copy(pattern="*", dst="include/hpx", src="%s/hpx" % self.folder, keep_path=True)
        
        self.copy(pattern="*.lib", dst="lib", src="%s/_build/lib" % self.folder, keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="%s/_build/lib" % self.folder, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src="%s/_build/lib" % self.folder, keep_path=False)
        self.copy(pattern="*.so.*", dst="lib", src="%s/_build/lib" % self.folder, keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", src="%s/_build/lib" % self.folder, keep_path=False)
        
        self.copy(pattern="*.dll", dst="bin", src="%s/_build/lib" % self.folder, keep_path=False)
        
        # Copy compilation tools
        self.copy(pattern="*", dst="resources/pkgconfig", src="%s/_build/lib/pkgconfig" % self.folder, keep_path=True)
        self.copy(pattern="*", dst="resources/pkgconfig", src="%s/_build/lib/pkgconfig" % self.folder, keep_path=True)
       
    def package_info(self):  
                
        self.cpp_info.libs = ["hpx", "hpx_serialization", "ag", "binpacking_factory", "cancelable_action", "component_storage", "distributing_factory",
                              "iostreams", "jacobi_component", "managed_accumulator", "memory", "nqueen", "parcel_coalescing", "random_mem_access", "remote_object",
                              "simple_accumulator", "simple_central_tuplespace", "sine", "startup_shutdown", "template_function_accumulator", "throttle", "unordered",
                              "vector"]
        
        if self.settings.build_type == "Debug":
            self.cpp_info.libs = [lib + "d" for lib in self.cpp_info.libs]
            
        
        if self.settings.os == "Linux":
            #self.cpp_info.libs.extend(["pthread","iostreams"])
            pass
        
        self.cpp_info.cflags = ["-std=c++11"]
        self.cpp_info.cppflags = ["-std=c++11"]
        
        self.cpp_info.defines.extend(["HPX_COMPONENT_EXPORTS", "HPX_ENABLE_ASSERT_HANDLER"])
