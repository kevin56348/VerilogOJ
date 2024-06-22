import os
import re
from distutils.core import Extension, setup
from Cython.Build import cythonize
from Cython.Compiler import Options


exclude_so = ['__init__.py', "setup.py"]
sources = ['./']

extensions = []
for source in sources:
    for dirpath, foldernames, filenames in os.walk(source):
        for filename in filter(lambda x: re.match(r'.*[.]py$', x), filenames):
            # print(filename)
            file_path = os.path.join(dirpath, filename)
            if filename not in exclude_so:
                print("debug point ", file_path[:-3].replace('/', '.')[2:])
                extensions.append(
                    Extension(file_path[:-3].replace('/', '.')[2:], [file_path], extra_compile_args=["-Os", "-g0"],
                              extra_link_args=["-Wl,--strip-all"]))


print("debug point 1")
Options.docstrings = False
compiler_directives = {'optimize.unpack_method_calls': False}
setup(
    ext_modules=cythonize(extensions, exclude=None, nthreads=20, quiet=True, build_dir='./build',
                          language_level=3, compiler_directives=compiler_directives))
print("bulid success")
