from conans import ConanFile
from conans import GCC, CMake
import os


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"
    requires = "hpx/0.9.11@lasote/stable"
    generators = "cmake", "gcc" # Generates conanbuildinfo.gcc with all deps information

    def build(self):
        if self.settings.build_type == "Debug":
            return True # I can't find any example that supports debug mode: https://github.com/STEllAR-GROUP/hpx/issues/1800
        
        cmake = CMake(self.settings)
        self.run('cmake . %s ' % cmake.command_line)
        self.run("cmake --build . %s " % cmake.build_config)

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")
        self.copy(pattern="*", dst="resources", src="resources")

    def test(self):
        if self.settings.build_type == "Debug":
            return True # I can't find any example that supports debug mode: https://github.com/STEllAR-GROUP/hpx/issues/1800
        self.run("cd bin && .%smytest" % (os.sep))
