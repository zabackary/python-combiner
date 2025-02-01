import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # only import these for the types because these two modules both depend on
    # `options.py` which depends on this file
    from ..processedmodule import ModuleUniqueIdentifierGenerator
    from ..transformers import FoundImport


class Plugin:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def hook_module(self, path: str, module: ast.Module) -> ast.Module:
        """ A hook run before name translation is performed and modules are bundled

        Note: this is run even for modules outside the current project, like
        library files. If you don't want this to run on those files, use `path`
        to perform a restriction.
        """
        return module

    def hook_module_post_transform(self, path: str, module: list[ast.stmt], name_generator: "ModuleUniqueIdentifierGenerator") -> list[ast.stmt]:
        """ A hook run after name translation is performed but before modules are bundled

        Generally you should not be using this, but it might be useful to perform 
        some transformation on the exports. It also receives the `ModuleUniqueIdentifierGenerator`
        instance needed to know how imports and exports are named.
        """
        return module

    def hook_import(self, imp: "FoundImport") -> "FoundImport":
        """ A hook run on all imports a module imports.

        This can be used to e.g. modify an import path.
        """
        return imp

    def hook_import_resolution(self, path: str, module: str) -> tuple[str, str] | None:
        """ A hook run during the module resolution step. 

        This hook is called with the module to be imported's name (`module`) as well
        as the path it was imported from (`path`). It should return either a)
        a tuple whose first element is the resolved source of the module and second
        element is the path of the imported module or the string "built-in" if it's
        generated or a stdlib module or b) None to fall back to the default
        resolution.
        """
        return None

    def hook_output(self, module: ast.Module) -> ast.Module:
        """ A hook called just prior to the end of code generation. """
        return module

    def hook_unparse(self, module: ast.Module) -> str | None:
        """ A hook called to customize unparsing. There can only be one of these. """
        return None
