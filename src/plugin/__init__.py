from .constants import ConstantsPlugin
from .plugin import Plugin
from .prelude import PreludePlugin
from .simplify_if import SimplifyIfPlugin

builtin_plugins = [ConstantsPlugin,
                   PreludePlugin, SimplifyIfPlugin]

__all__ = ["Plugin", "builtin_plugins",
           "ConstantsPlugin", "PreludePlugin", "SimplifyIfPlugin"]
