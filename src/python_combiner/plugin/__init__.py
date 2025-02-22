from .constants import ConstantsPlugin
from .plugin import Plugin
from .prelude import PreludePlugin
from .simplify_if import SimplifyIfPlugin

builtin_plugins = [ConstantsPlugin,
                   PreludePlugin, SimplifyIfPlugin]

try:
    import python_minifier as _
except ImportError:
    pass
else:
    from .minifier import MinifyPlugin
    builtin_plugins.append(MinifyPlugin)

__all__ = ["Plugin", "builtin_plugins"]
__all__ += [cls.__name__ for cls in builtin_plugins]
