# The content of this file is mostly copy-pasted from https://github.com/eliben/pyelftools/blob/main/examples/dwarf_decode_address.py

import fnmatch
import os
import pathlib
from glob import glob
import logging
from typing_extensions import Self

from .source_code_locator import SourceCodeLocator
from ..log import LOGGER_NAME

logger = logging.getLogger(os.path.relpath(LOGGER_NAME))


class SourceCodeFilesManager:
    """ """

    _instance = None
    _available_files = {}

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super(SourceCodeFilesManager, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.files: dict[str, list[str]] = {}
        self._initialized = True

    def find_available_source_files(self, directories: list[str]):
        for dir in directories:
            ls = glob(f"{dir}/**/*.c", recursive=True)
            c_files = fnmatch.filter(ls, "*.c")
            for file in c_files:
                n = pathlib.Path(file).name
                self._available_files[n] = file
        logger.info(f"Found {len(self._available_files)} C source files.")

    def load_file(self, file_path: pathlib.Path):
        try:
            with open(file_path) as f:
                lines = f.readlines()
        except FileNotFoundError as e:
            logger.warning(e)
            lines = []
        self.files[file_path.name] = lines

    def get_file_lines(
        self, file_path: pathlib.Path, start, end
    ) -> list[tuple[int, str]]:
        out = []
        file = self.files.get(file_path.name)
        a_file = self._available_files.get(file_path.name)
        if file is None:
            if a_file is not None:
                self.load_file(pathlib.Path(a_file))
            else:
                self.load_file(file_path)
            file = self.files[file_path.name]
        for line_number, line in enumerate(file, 1):
            if start <= line_number <= end:
                out.append((line_number, line))
        return out

    def get_source_lines(self, binary_file_name: str, address: int, sources_dirs):
        self.find_available_source_files(sources_dirs)
        locator = SourceCodeLocator(binary_file_name, binary_file_name)
        function_name, file_name, src_l = locator.find_location_in_source_code(address)
        if file_name is not None and src_l is not None:
            source_file_path = pathlib.Path(file_name)
            return self.get_file_lines(source_file_path, src_l, src_l)
        else:
            logger.info(f"No sources for address {address:x}")
            return []
        
    @classmethod
    def delete_instance(cls):
        cls._instance = None


