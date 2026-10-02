"""Auto-generate Justfile recipes from Typer CLI apps.

Introspects Typer CLI structure and generates corresponding justfile recipes.
Enables single source of truth: define CLI in Python, generate justfile automatically.

Philosophy: Typer is the source of truth; justfile is generated.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, get_type_hints

import typer


class TyperToJustfile:
    """Convert Typer app to Justfile recipes."""

    @staticmethod
    def generate(app: typer.Typer, module_name: str = "main") -> str:
        """Generate Justfile recipes from Typer app.

        Args:
            app: Typer app instance
            module_name: Python module name for CLI entry point

        Returns:
            Justfile content as string
        """
        lines = ["# Auto-generated from Typer CLI", "# Do not edit manually", ""]

        # Get all commands from the app
        commands = app.registered_commands

        for command in commands:
            recipe = TyperToJustfile._generate_recipe(
                command.callback,
                module_name,
            )
            lines.append(recipe)
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _generate_recipe(
        func: Callable,
        module_name: str,
    ) -> str:
        """Generate a single Justfile recipe from a Typer command.

        Args:
            func: Typer command function
            module_name: Python module name

        Returns:
            Justfile recipe as string
        """
        # Get function name (command name)
        command_name = func.__name__

        # Get docstring as comment
        docstring = inspect.getdoc(func) or ""
        comment_lines = ["# " + line for line in docstring.split("\n") if line.strip()]

        # Get function signature
        sig = inspect.signature(func)
        params = []
        flags = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            # Check if it's a typer.Option or typer.Argument
            annotation = param.annotation
            default = param.default

            if isinstance(default, typer.models.OptionInfo):
                # It's an option
                flag_name = default.param_decls[0] if default.param_decls else f"--{param_name}"
                flags.append(f'{flag_name} "{{{param_name}}}"')
            elif param_name not in ("typer", "ctx"):
                # It's a regular argument
                params.append(f"{{{param_name}}}")

        # Build recipe line
        recipe_params = " ".join(params)
        if recipe_params:
            recipe_header = f"{command_name} {recipe_params}"
        else:
            recipe_header = command_name

        recipe_content = f"uv run python -m {module_name} {command_name}"
        if flags or params:
            recipe_content += " " + " ".join(params + flags)

        # Build full recipe
        lines = comment_lines + [
            f"{recipe_header}:",
            f"    {recipe_content}",
        ]

        return "\n".join(lines)

    @staticmethod
    def write_justfile(app: typer.Typer, output_path: str) -> None:
        """Generate and write Justfile to disk.

        Args:
            app: Typer app instance
            output_path: Path to write justfile
        """
        content = TyperToJustfile.generate(app, "math_trace.cli")
        with open(output_path, "w") as f:
            f.write(content)


if __name__ == "__main__":
    # Test: generate justfile from our CLI
    from math_trace.cli import app

    print(TyperToJustfile.generate(app, "math_trace.cli"))
