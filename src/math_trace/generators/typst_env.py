"""Typst theorem/proof environment builders."""


class TypstEnvironmentBuilder:
    """Build Typst theorem/proof environments with proper formatting."""

    @staticmethod
    def theorem(
        name: str,
        title: str,
        statement: str,
        label: str | None = None,
    ) -> str:
        """
        Generate a Typst theorem environment.

        Args:
            name: Internal identifier
            title: Theorem title
            statement: Mathematical statement
            label: Optional label for cross-reference

        Returns:
            Typst theorem block
        """
        label_str = f"\n  label: <{label}>" if label else ""

        return f"""{name}: [#strong[{title}]][
  {statement}
]{label_str}
"""

    @staticmethod
    def proof(body: str) -> str:
        """
        Generate a Typst proof environment.

        Args:
            body: Proof text and equations

        Returns:
            Typst proof block
        """
        return f"""#proof[
  {body}
  #qed
]
"""
