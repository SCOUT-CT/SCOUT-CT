import importlib
from typing import Type, TypeVar

from angr import Project, SimProcedure

T = TypeVar("T", bound=SimProcedure)


def load_hooks(project: Project, plugin: str, symbol_names: list[str]):
    for n in symbol_names:
        dotted_path = f"{plugin}.{n}"
        SimProcedureClass = import_from_string(dotted_path)
        add_hook(project, SimProcedureClass, n)


def add_hook(project: Project, cls: Type[T], symbol_name: str):
    instance = cls()
    project.hook_symbol(symbol_name, instance)


def import_from_string(dotted_path: str):
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
