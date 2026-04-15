import angr

def pc_offset(program_state: angr.SimState) -> int:
    """
    Returns the offset of the program counter (PC) from the binary's base address.
    """
    binary_address = program_state.project.loader.main_object.image_base_delta # type: ignore
    return program_state.addr - binary_address