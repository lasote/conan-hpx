from conans import ConanFile
from conans.tools import download, unzip
import os
import shutil
from conans import CMake

class HPXConan(ConanFile):
    name = "hpx"
    version = "0.9.10"
    folder = "hpx_%s" % version
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = "CMakeLists.txt"
    generators = "cmake"
    url="http://github.com/lasote/conan-hpx"
    requires = "boost/1.59.0@lasote/stable", "hwloc/1.11.1@lasote/stable"

    def config(self):
        pass
    
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
         # Build
        self.run("cd %s &&  mkdir _build" % self.folder)
        configure_command = 'cd %s/_build && cmake .. %s' % (self.folder, cmake.command_line)
        self.output.warn("Configure with: %s" % configure_command)
        self.run(configure_command)
        self.run("cd %s/_build && cmake --build . %s" % (self.folder, cmake.build_config))

    def replace_in_file(self, file_path, search, replace):
        with open(file_path, 'r') as content_file:
            content = content_file.read()
            content = content.replace(search, replace)
        with open(file_path, 'wb') as handle:
            handle.write(content)

    def package(self):
        """ Define your conan structure: headers, libs and data. After building your
            project, this method is called to create a defined structure:
        """
        self.copy(pattern="*.h", dst="include", src="%s/_build/include" % self.folder, keep_path=False)
        self.copy(pattern="*.h", dst="include", src="%s/include" % self.folder, keep_path=False)
        
        # Win
        self.copy(pattern="*.dll", dst="bin", src="%s/_build/" % self.folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="%s/_build/" % self.folder, keep_path=False)
        
        # UNIX
        if self.settings.os != "Windows":
            if not self.options.shared:
                self.copy(pattern="*.a", dst="lib", src="%s/build/" % self.folder, keep_path=False)
                self.copy(pattern="*.a", dst="lib", src="%s/build/.libs/" % self.folder, keep_path=False)   
            else:
                self.copy(pattern="*.so*", dst="lib", src="%s/build/.libs/" % self.folder, keep_path=False)
                self.copy(pattern="*.dylib*", dst="lib", src="%s/build/.libs/" % self.folder, keep_path=False)

    def package_info(self):  
                
        self.cpp_info.libs = ["hpx"]