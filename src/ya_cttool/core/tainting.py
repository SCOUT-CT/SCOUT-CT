import angr
import claripy

from .models import Color

# An angr symbolic expression is a tree whose leafs are symbols or concrete values and other nodes are operations (addition,
# concatenation, ...).
# An angr symbolic expression is an instance of `claripy.ast.Base` and an angr symbolic expression representing a sequence of
# bits is an instance of `claripy.ast.BV` (BV stands for bit vector).
# Fresh symbols are created using claripy.BVS(<symbol name>, <size in bits>). The symbol will get a name starting with
# <symbol name> but with other content appended to it to make its name unique.
# Expression are built by angr as the resul of operations that involve symbols.
# <symbolic expression>.variables is a collection of the names of all the symbols this expression depends on.

# We can easily build a tainting propagation system on top of the symbolic expression system of angr : we assign a symbol to
# the source of a taint, with a name identifying the taint. Then all memory area to which the taint is propagated are assigned
# a symbolic expression by angr. We determine which taint has contaminated a symbolic data using <expression>.variables.

# Secret dependent data
RED_TAINT_SYMBOL_NAME = 'red_taint'
# Potential secret dependent data
ORANGE_TAINT_SYMBOL_NAME = 'orange_taint'
# Non-secret dependent data with unknown value
GREEN_TAINT_SYMBOL_NAME = 'green_taint'

def _is_red_symbol_name(symbol_name: str) -> bool:
    return RED_TAINT_SYMBOL_NAME in symbol_name


def _is_orange_symbol_name(symbol_name: str) -> bool:
    return ORANGE_TAINT_SYMBOL_NAME in symbol_name


def _is_green_symbol_name(symbol_name: str) -> bool:
    return GREEN_TAINT_SYMBOL_NAME in symbol_name


def _build_red_taint_symbol(size_bytes: int = 1) -> claripy.ast.BV:
    """
    Returns a symbolic expression representing a source of red taint.
    """
    return claripy.BVS(RED_TAINT_SYMBOL_NAME, size_bytes * 8)


def _expression_depends_on_red_symbol(expression: claripy.ast.BV) -> bool:
    """
    Checks if an expression represents data that depends on a source of red taint.
    """
    return any(_is_red_symbol_name(variable) for variable in expression.variables)


def _build_orange_taint_symbol(size_bytes: int = 1) -> claripy.ast.BV:
    """
    Returns a symbolic expression representing a source of orange taint.
    """
    return claripy.BVS(ORANGE_TAINT_SYMBOL_NAME, size_bytes * 8)


def _expression_depends_on_orange_symbol(expression: claripy.ast.BV) -> bool:
    """
    Checks if an expression represents data that depends on a source of orange taint.
    """
    return any(_is_orange_symbol_name(variable) for variable in expression.variables)


def _build_green_taint_symbol(size_bytes: int = 1) -> claripy.ast.BV:
    """
    Returns a symbolic expression representing a source of green taint.
    """
    return claripy.BVS(GREEN_TAINT_SYMBOL_NAME, size_bytes * 8)


def _expression_depends_on_green_symbol(expression: claripy.ast.BV) -> bool:
    """
    Checks if an expression represents data that depends on a source of green taint.
    """
    return any(_is_green_symbol_name(variable) for variable in expression.variables)


def build_expression_for_status(status: Color | int, size_bytes: int = 1) -> claripy.ast.BV:
    """
    Builds an angr symbolic expression for representing the desired data status : red / orange / green taint.

    In our analysis, we use symbolic data to represent the red tainted bytes (secret dependent), orange tainted bytes (potentially
    secret dependent), or green tainted bytes (unknown non-secret-dependent value). This function expects `status` to be either
    'red', 'orange', 'green', or a concrete number. It returns an appropriate symbolic expression to represent data with this
    status.
    """
    
    if status == Color.Red:
        return _build_red_taint_symbol(size_bytes)

    if status == Color.Orange:
        return _build_orange_taint_symbol(size_bytes)

    if status == Color.Green:
        return _build_green_taint_symbol(size_bytes)

    if isinstance(status, int):
        return claripy.BVV(status, size_bytes * 8)

    # a data status is either red tainted, orange tainted, green tainted, or a concrete value
    assert False


def status_from_expression(expression: int | claripy.ast.BV, program_state: angr.SimState) -> Color | int:
    """
    Finds the data status represented by an angr symbolic expression.

    In our analysis, we use symbolic data to represent the red tainted bytes (secret dependent), orange tainted bytes (potentially
    secret dependent) and green tainted bytes (unknown non-secret-dependent value).

    This function returns either 'red', 'orange', 'green', or an actual int, depending on the status determined by `expression`.

    `expression` may represent a symbolic boolean instead of a bitvector, in which case this function may return a boolean.
    """
    if isinstance(expression, int):
        return expression

    # if `expression` is not an int, it is an angr expression 
    if not isinstance(expression, claripy.ast.Base):
        raise ValueError

    # an angr expression can actually represent a concrete value
    if expression.concrete:
        # for some reason, expression.concrete_value can crash even if expression is concrete, so we rely on the solver instead
        return expression.concrete_value
        #return program_state.solver.eval_one(expression)

    # Make sure that we are only dealing with symbols that we have produced, not with other symbols produced by angr
    # automatically.
    for variable in expression.variables:
        if not (
                _is_red_symbol_name(variable)
                or _is_orange_symbol_name(variable)
                or _is_green_symbol_name(variable)
        ):
            print(f"\n\nVariable name : {variable}\n\n")
            raise ValueError("Uncontrolled symbol encountered")


    # If at least one red tainted value is involved in the computation of the data, then the tainting state of the data is red,
    # as it is guaranteed to depend on the secret.
    if _expression_depends_on_red_symbol(expression):
        return Color.Red
    # If the data does not depend on any red tainted value but it depends on at least one orange tainted value, then its tainting
    # state is orange as it may depend on the secret.
    elif _expression_depends_on_orange_symbol(expression):
        return Color.Orange
    # If the data does not depend on the secret but depends on data with unknown value, it itself has an unknown value, i.e.,
    # it is green tainted
    elif _expression_depends_on_green_symbol(expression):
        return Color.Green
    else:
        raise ValueError


def get_over_approximation_of_statuses(status1: Color | int, status2: Color | int) -> Color | int:
    """
    From a pair of data statuses, gives a data status that over-approximates them.

    A data status is either 'red' for secret-dependent data, 'orange' for potentially secret-dependent data, 'green' for
    non-secret-dependent data with unknown value or a concrete value. This function finds the over-approximation that should be
    used when two program states are merged during the analysis.

    The following over-approximation rules are used:
    - The over-approximated status is the orange taint whenever one of the two statuses is the orange taint or one is the red
    taint and the other is non secret dependent
    - The over-approximated status is the green taint if none of the two statuses is secret-dependent and one of them is the
    green taint
    """

    # todo: clarify what happens here, maybe the None case should be handled by the caller ?
    if status1 is None:
        status1 = 0
    if status2 is None:
        status2 = 0

    if status1 == status2:
        return status1

    # orange-red, orange-green and orange-concrete are over-approximated as orange
    elif status1 == Color.Orange or status2 == Color.Orange:
        return Color.Orange

    # red-green and red-concrete are over-approximated as orange
    elif status1 == Color.Red or status2 == Color.Red:
        return Color.Orange

    # green-concrete is over-approximated as green
    elif status1 == Color.Green or status2 == Color.Green:
        return Color.Green

    # concrete-concrete is over-approximated as green
    elif isinstance(status1, int) and isinstance(status2, int):
        return Color.Green

    else:
        raise ValueError
