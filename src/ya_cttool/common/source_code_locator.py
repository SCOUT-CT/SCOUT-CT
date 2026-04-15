from typing_extensions import Self
import logging
import os

from elftools.dwarf.lineprogram import LineProgram
from elftools.dwarf.descriptions import describe_form_class
from elftools.elf.elffile import ELFFile

from ..log import LOGGER_NAME

logger = logging.getLogger(os.path.relpath(LOGGER_NAME))


class SourceCodeLocator:
    """ """

    _instances: dict[str, Self] = {}

    def __new__(cls, key: str, *args, **kwargs) -> Self:
        if key in cls._instances:
            return cls._instances[key]
        instance = super().__new__(cls)
        cls._instances[key] = instance
        return instance

    def __init__(self, key: str, bin_path: str):
        """Constructor

        Args:
            key (str): used to retrieve the instance later
            bin_path (str): the binary file containing debug infos
        """
        # Be careful: __init__ is called every time even if __new__ returns existing
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.key = key
        with open(bin_path, "rb") as f:
            elffile = ELFFile(f)
            if elffile.has_dwarf_info():
                self.dwarf_info = elffile.get_dwarf_info()
            else:
                logger.warning(f"{bin_path} does not contain debug infos.")
                self.dwarf_info = None
        self._initialized = True

    def find_location_in_source_code(
        self, address: int
    ) -> tuple[str | None, str | None, int | None]:
        """Find location in source code using DWARF infos.

        Args:
            address (int): The address to retrieve the information from

        Returns:
            tuple[str | None, str | None, int | None]: function name, source file name, line number
        """
        funcname = self._decode_func_name(address)
        file, line = self._decode_file_line(address)
        if file is not None:
            file = file.decode("utf-8")
        return funcname, file, line

    def _decode_func_name(self, address: int) -> str | None:
        # Go over all DIEs in the DWARF information, looking for a subprogram
        # entry with an address range that includes the given address. Note that
        # this simplifies things by disregarding subprograms that may have
        # split address ranges.

        if self.dwarf_info is None:
            return None

        for CU in self.dwarf_info.iter_CUs():
            for DIE in CU.iter_DIEs():
                if (
                    DIE.tag == "DW_TAG_subprogram"
                    and DIE.attributes.get("DW_AT_low_pc") is not None
                ):
                    lowpc = DIE.attributes["DW_AT_low_pc"].value
                    # DWARF v4 in section 2.17 describes how to interpret the
                    # DW_AT_high_pc attribute based on the class of its form.
                    # For class 'address' it's taken as an absolute address
                    # (similarly to DW_AT_low_pc); for class 'constant', it's
                    # an offset from DW_AT_low_pc.
                    if DIE.attributes.get("DW_AT_high_pc") is None:
                        continue
                    highpc_attr = DIE.attributes["DW_AT_high_pc"]
                    highpc_attr_class = describe_form_class(highpc_attr.form)
                    if highpc_attr_class == "address":
                        highpc = highpc_attr.value
                    elif highpc_attr_class == "constant":
                        highpc = lowpc + highpc_attr.value
                    else:
                        logger.error(
                            f"Error: invalid DW_AT_high_pc class: {highpc_attr_class}"
                        )
                        continue

                    if lowpc <= address < highpc:
                        if DIE.attributes.get("DW_AT_name") is not None:
                            return DIE.attributes["DW_AT_name"].value
        return None

    def _decode_file_line(self, address) -> tuple[bytes | None, int | None]:
        # Go over all the line programs in the DWARF information, looking for
        # one that describes the given address.

        if self.dwarf_info is None:
            return None, None

        for CU in self.dwarf_info.iter_CUs():
            # First, look at line programs to find the file/line for the address
            lineprog: LineProgram | None = self.dwarf_info.line_program_for_CU(CU)
            if lineprog is None:
                continue
            delta = 1 if lineprog.header.version < 5 else 0
            prevstate = None
            for entry in lineprog.get_entries():
                # We're interested in those entries where a new state is assigned
                if entry.state is None:
                    continue
                # Looking for a range of addresses in two consecutive states that
                # contain the required address.
                if prevstate and prevstate.address <= address < entry.state.address:
                    filename = lineprog["file_entry"][prevstate.file - delta].name
                    line = prevstate.line
                    return filename, line
                if entry.state.end_sequence:
                    # For the state with `end_sequence`, `address` means the address
                    # of the first byte after the target machine instruction
                    # sequence and other information is meaningless. We clear
                    # prevstate so that it's not used in the next iteration. Address
                    # info is used in the above comparison to see if we need to use
                    # the line information for the prevstate.
                    prevstate = None
                else:
                    prevstate = entry.state
        return None, None

    @classmethod
    def delete_instances(cls):
        cls._instances = {}
