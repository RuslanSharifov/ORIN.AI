"""Strict validation for model-supplied tool arguments (no coercion)."""

import inspect
import math
from collections.abc import Mapping
from typing import Any, get_type_hints


class InvalidToolArguments(ValueError):
    """Tool input did not match its declared Python signature."""


def validate_arguments(handler: Any, arguments: Mapping[str, Any]) -> dict[str, Any]:
    """Bind keyword arguments and enforce simple annotated parameter types.

    Unsupported annotations fail closed. No arbitrary nested objects or
    variadic parameters are accepted. More complex tools will require a
    versioned schema contract in a later iteration.
    """
    if len(arguments) > 20:
        raise InvalidToolArguments("Too many arguments")
    for key, value in arguments.items():
        if not isinstance(key, str) or len(key) > 80:
            raise InvalidToolArguments("Invalid argument name")
        if isinstance(value, str) and len(value) > 4096:
            raise InvalidToolArguments("String argument too long")
    try:
        signature = inspect.signature(handler)
        hints = get_type_hints(handler)
    except (TypeError, ValueError, NameError) as exc:
        raise InvalidToolArguments("Tool signature is unavailable") from exc
    if any(
        p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        for p in signature.parameters.values()
    ):
        raise InvalidToolArguments("Variadic or positional-only tools are unsupported")
    try:
        bound = signature.bind(**arguments)
    except TypeError as exc:
        raise InvalidToolArguments("Missing or unexpected arguments") from exc
    for name, value in bound.arguments.items():
        expected = hints.get(name)
        if expected not in (str, int, float, bool):
            raise InvalidToolArguments(f"Unsupported or missing type annotation: {name}")
        if expected is int:
            valid = type(value) is int
        elif expected is float:
            valid = type(value) in (float, int) and math.isfinite(value)
        else:
            valid = type(value) is expected
        if not valid:
            raise InvalidToolArguments(f"Incorrect type for argument: {name}")
    return dict(bound.arguments)
