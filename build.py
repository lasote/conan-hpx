import os
import platform
import sys

if __name__ == "__main__":
    os.system('conan export lasote/stable')
   
    def test(settings):
        argv =  " ".join(sys.argv[1:])
        command = "conan test %s %s" % (settings, argv)
        retcode = os.system(command)
        if retcode != 0:
            exit("Error while executing:\n\t %s" % command)

    if platform.system() == "Windows":
        compiler = '-s compiler="Visual Studio" -s compiler.version=12 '
        # Static x86
        test(compiler + '-s arch=x86 -s build_type=Debug -s compiler.runtime=MDd')
        test(compiler + '-s arch=x86 -s build_type=Release -s compiler.runtime=MD')

        # Static x86_64
        test(compiler + '-s arch=x86_64 -s build_type=Debug -s compiler.runtime=MDd')
        test(compiler + '-s arch=x86_64 -s build_type=Release -s compiler.runtime=MD')

    else:  # Compiler and version not specified, please set it in your home/.conan/conan.conf (Valid for Macos and Linux)
        test('-s build_type=Release -s arch=x86_64')
        test('-s build_type=Debug -s arch=x86_64')
        
        if platform.system != "Darwin":
            test('-s build_type=Debug -s arch=x86')
            test('-s build_type=Release -s arch=x86')
