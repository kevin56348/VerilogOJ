from __future__ import absolute_import
from __future__ import print_function
# from pprint import pprint
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

def convert_ports_to_ansi(module_def):
    ports = []
    items_to_remove = []
    portlist = module_def.portlist.ports
    port_names = set()
    for port in portlist:
        first = port.first if port.first is not None else pyverilog.vparser.ast.Inout(
            pyverilog.vparser.ast.Variable('<<unk_name?>>'))
        second = port.second if port.second is not None else pyverilog.vparser.ast.Wire(
            pyverilog.vparser.ast.Variable('<<unk_name?>>'))
        port = pyverilog.vparser.ast.Ioport(first=first, second=second, lineno=port.lineno)
        if port.first is not None:
            port_names.add(port.first.name)

        ports.append(port)
        # if isinstance(ioitem, vast.Ioport):
    new_portlist = vast.Portlist(tuple(ports))
    module_def.portlist = new_portlist

    # pprint(port_names)

    for item in module_def.items:
        if isinstance(item, (vast.Wire, vast.Reg)):
            for signal in item.list:
                if signal.name in port_names:
                    items_to_remove.append(signal)

    module_def.items = [item for item in module_def.items
                        if not any(signal.name in port_names for signal in getattr(item, 'list', []))]


def main():
    optparser = OptionParser()
    (options, args) = optparser.parse_args()
    filelist = args
    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)

    ast, directives = parse(filelist)

    # Traverse the AST to find all ModuleDefs
    modules = traverse_ast(ast, "ModuleDef", [])

    for module in modules:
        convert_ports_to_ansi(module)

    codegen = ASTCodeGenerator()
    rslt = codegen.visit(ast)
    print(rslt)


if __name__ == '__main__':
    main()