from conans import ConanFile
from conans import GCC, CMake
import os


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"
    requires = "hpx/0.9.10@lasote/stable"
    generators = ["cmake", "gcc"] # Generates conanbuildinfo.gcc with all deps information

    def build(self):
        if self.settings.os == "Linux":
            # EXAMPLE OF USE OF GCC, IT CAN BE COMPILED WITH CMAKE TOO
            gcc = GCC(self.settings)
            self.run("mkdir -p bin")
            command = 'gcc sdl_timer.c @conanbuildinfo.gcc -o bin/timer %s' % gcc.command_line
            self.output.warn(command)
            self.run(command)
        else:
            cmake = CMake(self.settings)
            self.run('cmake . %s' % cmake.command_line)
            self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")

    def test(self):
        self.run("cd bin && .%stimer" % (os.sep))