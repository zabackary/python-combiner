import argparse
import json
import os
import sys
import time

from python_compiler import Compiler, CompilerOptions, errors, plugin

DEFAULT_FILE_NAME = "__stdin__.py"
PROG_NAME = "python-compiler"


def format_error(name: str, msg: str, output_json: bool = False):
    if output_json:
        return json.dumps({
            "error": True,
            "name": name,
            "msg": msg
        })
    else:
        return f"{errors._terminal_colors.BOLD}{PROG_NAME}: error({errors._terminal_colors.FAIL}{name}{errors._terminal_colors.ENDC}{errors._terminal_colors.BOLD}):{errors._terminal_colors.ENDC} {msg}"


def format_compiler_error(error: errors.CompilerError, output_json: bool = False):
    return format_error(error.errcode, str(error), output_json)


def main(argv: list[str] | None = None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog=PROG_NAME,
        description="Compiles/merges Python files.")
    parser.add_argument("-i", "--input", required=True,
                        type=argparse.FileType('r'),
                        help="the input file, can be - for stdin")
    parser.add_argument("-o", "--output", nargs="?",
                        type=argparse.FileType('w'), default=sys.stdout,
                        help="the output file. Defaults to stdout")
    parser.add_argument("--ignore-imports", nargs="+",
                        default=[],
                        help="modules for which to ignore transforming imports for (i.e., leave them untouched)")
    parser.add_argument("--remove-imports", nargs="+",
                        default=[],
                        help="modules for which to remove imports for")
    parser.add_argument("-p", "--prelude",
                        default=None,
                        help="some Python code to insert at the top of the file. must be well-formed parsable Python code")
    parser.add_argument("-c", "--define-constant", nargs=2,
                        default=[],
                        action="append",
                        help="defines one compile-time constant as a string. use some name that you're sure won't collide with any in your code, i.e. __MY_CONSTANT__")
    parser.add_argument("-d", "--define", nargs=1,
                        default=[],
                        action="append",
                        help="equivalent to defining a constant to be 1 using --define-constant.")
    parser.add_argument("-m", "--minify", action=argparse.BooleanOptionalAction,
                        help="minifies the result")
    parser.add_argument("-j", "--json", action=argparse.BooleanOptionalAction,
                        help="outputs messages as json")
    parser.add_argument("-t", "--time", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="puts the time at the top of the generated code. --no-time for deterministic builds")
    parser.add_argument("--docstring", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="puts a generated docstring at the top of the module. added by default")
    parser.add_argument("--module-hash-length",
                        type=int,
                        default=8,
                        help="the length of the hash used for making modules unique")
    parser.add_argument("--export-dictionary-mode",
                        default="dict",
                        choices=["dict", "munch", "class", "class_instance"],
                        help="the method that export dictionaries are converted to dot-accessible objects")
    parser.add_argument("--export-names-mode",
                        default="locals",
                        choices=["locals", "static"],
                        help="how module exports are determined. use 'locals' for compatibility with existing code. forced to 'static' if --export-dictionary-mode is set to 'class' or 'class_instance'")
    args = parser.parse_args(argv)
    constants: dict[str, bool | str | int | float] = {
        "__COMPILED__": True
    }
    for [constant_name, constant_value] in args.define_constant:
        if constant_value.lower() == "true":
            constants[constant_name] = True
        elif constant_value.lower() == "false":
            constants[constant_name] = False
        else:
            try:
                if "." in constant_value:
                    constants[constant_name] = float(constant_value)
                else:
                    constants[constant_name] = int(constant_value)
            except ValueError:
                constants[constant_name] = constant_value
    for [constant_name] in args.define:
        constants[constant_name] = 1
    current_time = (" at %s" % time.strftime(
        "%a, %d %b %Y %H:%M:%S", time.localtime())) if args.time else ""
    with args.input as input:
        try:
            plugins: list[plugin.Plugin] = []
            plugins.append(plugin.ConstantsPlugin(constants=constants))
            plugins.append(plugin.SimplifyIfPlugin())
            if args.prelude is not None:
                plugins.append(plugin.PreludePlugin(prelude=args.prelude))
            # if args.minify:
            #    plugins.append(plugin.MinifyPlugin())
            merged = Compiler(
                source=input.read(),
                path=os.path.join(os.getcwd(),
                                  input.name if input.name != "<stdin>" else DEFAULT_FILE_NAME),
                options=CompilerOptions(
                    ignore_imports=args.ignore_imports,
                    remove_imports=args.remove_imports,
                    docstring=f""" Generated by {PROG_NAME}{
                        current_time} """ if args.docstring else None,
                    export_dictionary_mode=args.export_dictionary_mode,
                    export_names_mode=args.export_names_mode,
                    short_generated_names=args.minify,
                    hash_length=args.module_hash_length,
                    plugins=plugins
                ))()
            if args.json:
                if args.output.name == "<stdout>":
                    args.output.write(json.dumps({
                        "output": merged
                    }))
                else:
                    args.output.write(merged)
            else:
                args.output.write(merged)
        except errors.CompilerError as err:
            print(
                format_compiler_error(err, args.json),
                file=sys.stderr)
            sys.exit(1)
        except plugin.constants.AssignmentToConstantError as err:
            print(
                format_error("assignment-to-constant", str(err), args.json),
                file=sys.stderr)
            sys.exit(1)
