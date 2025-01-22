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
    for c in ast.children():
        traverse_ast(c, typex, x)
    if ast.__class__.__name__ == typex:
        x.append(ast)
    return x

def convert_ports_to_ansi(module_def):
    ports = []
    new_items = []
    items_to_remove = []
    portlist = module_def.portlist.ports
    port_names = set()

    for port in module_def.portlist.ports:
        first = port.first if port.first is not None else pyverilog.vparser.ast.Inout(pyverilog.vparser.ast.Variable('<<unk_name?>>'))
        second = port.second if port.second is not None else pyverilog.vparser.ast.Wire(pyverilog.vparser.ast.Variable('<<unk_name?>>'))
        port = pyverilog.vparser.ast.Ioport(first=first, second=second, lineno=port.lineno)
        if port.first is not None: port_names.add(port.first.name)

        ports.append(port)

    new_portlist = pyverilog.vparser.ast.Portlist(tuple(ports))
    module_def.portlist = new_portlist

    for item in module_def.items:
        if not isinstance(item, pyverilog.vparser.ast.Decl): continue
        for signal in item.list:
            if isinstance(signal, (pyverilog.vparser.ast.Wire, pyverilog.vparser.ast.Reg)) and signal.name in port_names:
                items_to_remove.append(signal)

    for item in module_def.items:
        if not isinstance(item, pyverilog.vparser.ast.Decl):
            new_items.append(item)
            continue

        filtered_signals = [signal for signal in item.list if signal not in items_to_remove]
        if filtered_signals:
            new_items.append(pyverilog.vparser.ast.Decl(filtered_signals))

    module_def.items = new_items

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
