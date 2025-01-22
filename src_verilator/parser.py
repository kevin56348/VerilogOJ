from __future__ import absolute_import
from __future__ import print_function
import sys
import os
from optparse import OptionParser

import pyverilog
from pyverilog.vparser.parser import parse
import pyverilog.vparser.ast as vast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator


def traverse_ast(ast, typex, x):
    # find module def
    for c in ast.children():
        traverse_ast(c, typex, x)
    if ast.__class__.__name__ == typex:
        x.append(ast)
    return x


def main():
    optparser = OptionParser()
    (options, args) = optparser.parse_args()

    filelist = args
    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)

    ast, directives = parse(filelist)

    ast.show()

    # generate code
    # # no params, we assume
    # params = vast.Paramlist(())
    #
    # ports = vast.Portlist(tuple(ioports))
    #
    # moduledef = traverse_ast(ast, "ModuleDef", [])[0]
    #
    # ast = vast.ModuleDef(moduledef.name, params, ports, tuple(decls))
    #
    # codegen = ASTCodeGenerator()
    # rslt = codegen.visit(ast)
    # print(rslt)


if __name__ == '__main__':
    main()
