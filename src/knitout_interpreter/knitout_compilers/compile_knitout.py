"""used to run js DAT compiler"""
import platform
from enum import Enum

import importlib_resources

import knitout_interpreter


class Knitout_to_Machine_Compiler(Enum):
    """Enumeration of available knitout compilers."""
    SS_DAT_Compiler = 'knitout-to-dat.js'
    Kniterate_Compiler = 'knitout-to-kcode.js'


def _get_compiler(compiler_name: Knitout_to_Machine_Compiler | None = None):
    if compiler_name is None:
        compiler_name = Knitout_to_Machine_Compiler.SS_DAT_Compiler
    pg_resource_stream = importlib_resources.files(knitout_interpreter.knitout_compilers).joinpath(compiler_name.value)
    # assert pg_resource_stream.is_file()
    return pg_resource_stream


def compile_knitout(knitout_file_name: str, output_file_name: str | None = None, compiler: Knitout_to_Machine_Compiler | None = None) -> bool:
    """

    :param knitout_file_name: The name of the knitout file to process.
    :param output_file_name: The name of the output file to create. DAT files for Shima Seiki.
    :param compiler: The compiler type to use. Defaults to Shima Seiki DAT compiler.
    :return: True if the compiler was successful, False otherwise.
    """
    js_compiler_file = _get_compiler(compiler)
    print(f"\n################Converting {knitout_file_name} to DAT file {output_file_name} ########\n")
    if platform.system() == "Windows":
        # Run Node.js and return the exit code.
        from knitout_interpreter.knitout_compilers.run_js_dat_compilers_windows import run_js_compiler_windows
        return run_js_compiler_windows(output_file_name, js_compiler_file, knitout_file_name)
    else:
        from knitout_interpreter.knitout_compilers.run_js_dat_compilers_unix import run_js_compiler_unix
        return run_js_compiler_unix(output_file_name, js_compiler_file, knitout_file_name)
