import os
import platform
import sys

if __name__ == "__main__":
    os.system('conan export lasote/stable')
   
    def test(settings):
        argv =  " ".join(sys.argv[1:])
        argv = argv.replace("Visual Studio", '"Visual Studio"')
        command = "conan test %s %s" % (argv, settings)
        retcode = os.system(command)
        if retcode != 0:
            exit("Error while executing:\n\t %s" % command)

    if platform.system() == "Windows":
        # x86_64
        for compiler_version in ("12", ):
            compiler = '-s compiler="Visual Studio" -s compiler.version=%s ' % compiler_version
       
            test(compiler + '-s arch=x86_64 -s build_type=Release -s compiler.runtime=MD')
            test(compiler + '-s arch=x86_64 -s build_type=Debug -s compiler.runtime=MDd')

    else:  # Compiler and version not specified, please set it in your home/.conan/conan.conf (Valid for Macos and Linux)
        test('-s build_type=Release -s arch=x86_64')
        test('-s build_type=Debug -s arch=x86_64')
