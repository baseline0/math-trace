"""Auto-generate FastAPI routes from Typer CLI apps.

Mirrors TyperToJustfile pattern: Typer is source of truth, FastAPI is generated.
Enables single codebase to serve both CLI and web interfaces.

Philosophy: Define API once in Typer; get CLI + web endpoints automatically.
"""

from __future__ import annotations

import inspect
from typing import Callable, Optional


class TyperToFastAPI:
    """Convert Typer app to FastAPI routes."""

    @staticmethod
    def generate_route_code(
        func: Callable,
        method: str = "POST",
    ) -> str:
        """Generate a single FastAPI route from a Typer command.

        Args:
            func: Typer command function
            method: HTTP method (POST, GET, etc.)

        Returns:
            FastAPI route code as string
        """
        command_name = func.__name__
        docstring = inspect.getdoc(func) or ""

        # Get function signature
        sig = inspect.signature(func)
        params = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            annotation = param.annotation
            default = param.default

            # Build parameter with type hint
            type_hint = (
                annotation.__name__
                if hasattr(annotation, "__name__")
                else str(annotation)
            )

            if default is inspect.Parameter.empty:
                params.append(f"{param_name}: {type_hint}")
            else:
                params.append(f"{param_name}: {type_hint} = None")

        params_str = ", ".join(params)
        route_path = f"/api/{command_name.replace('_', '-')}"

        # Build route code
        lines = [
            f'@app.{method.lower()}("{route_path}")',
            f'async def route_{command_name}({params_str}):',
            f'    """',
            f'    {docstring.split(chr(10))[0]}',
            f'    """',
            f'    try:',
            f'        result = {command_name}({", ".join(p.split(":")[0].strip() for p in params.split(", ") if p)})',
            f'        return {{"status": "success", "data": result}}',
            f'    except Exception as e:',
            f'        return {{"status": "error", "message": str(e)}}',
        ]

        return "\n".join(lines)

    @staticmethod
    def generate_routes(app_module_path: str) -> str:
        """Generate FastAPI routes from a Typer app module.

        Args:
            app_module_path: Module path (e.g., "math_trace.cli")

        Returns:
            FastAPI route definitions as string
        """
        lines = [
            "# Auto-generated FastAPI routes from Typer CLI",
            "# Do not edit manually",
            "",
            "from fastapi import FastAPI",
            "from fastapi.responses import HTMLResponse",
            "",
            "app = FastAPI()",
            "",
        ]

        # Note: Full implementation would import and introspect the Typer app
        # For now, return template that can be extended
        return "\n".join(lines)
