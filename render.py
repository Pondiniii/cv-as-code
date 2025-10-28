#!/usr/bin/env python3
"""Render LaTeX template with Jinja2 from TOML data."""

import importlib
import re
from pathlib import Path

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for 3.10-
    try:
        tomllib = importlib.import_module("tomli")  # type: ignore[assignment]
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit(
            "tomllib module not found. Use Python 3.11+ or `pip install tomli`."
        ) from exc

from jinja2 import Environment, FileSystemLoader

def markdown_bold_to_latex(text):
    """Convert **text** to \\textbf{text} and escape % and $ signs."""
    # Escape special LaTeX characters first
    text = text.replace('%', '\\%')
    text = text.replace('$', '\\$')
    # Then convert **text** to \textbf{text}
    return re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)


def pipe_separate(value):
    """Join comma-delimited text with colored pipes for LaTeX output."""
    if isinstance(value, list):
        parts = value
    else:
        parts = [piece.strip() for piece in re.split(r',', value)]

    processed = []
    for part in parts:
        if not part:
            continue
        item = markdown_bold_to_latex(str(part))
        item = item.replace('/', '/\\allowbreak{}')
        processed.append(item)

    if not processed:
        return ''

    separator = ' {\\color{divider}|} '
    return separator.join(processed)


def metrics_inline(values):
    """Format project metrics inline with bold emphasis."""
    if not values:
        return ''

    parts = []
    for value in values:
        text = markdown_bold_to_latex(str(value))
        text = text.replace('\\\\%', '\\%').replace('\\\\$', '\\$')
        parts.append(f"\\textbf{{{text}}}")

    separator = ' \\textcolor{divider}{•} '
    return separator.join(parts)

def main():
    # Load data
    data_path = Path("cv.toml")
    with data_path.open("rb") as f:
        data = tomllib.load(f)

    # Setup Jinja2 with LaTeX-friendly delimiters
    env = Environment(
        loader=FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True,
        block_start_string="<BLOCK>",
        block_end_string="</BLOCK>",
        variable_start_string="<VAR>",
        variable_end_string="</VAR>",
        comment_start_string="<#",
        comment_end_string="#>",
    )

    # Add custom filter
    env.filters['bold'] = markdown_bold_to_latex
    env.filters['pipes'] = pipe_separate
    env.filters['metrics'] = metrics_inline

    # Render template
    template = env.get_template("base.tex.j2")
    output = template.render(**data)

    # Write output
    with open("output/cv.tex", "w") as f:
        f.write(output)

    print("✓ Rendered: output/cv.tex")

if __name__ == "__main__":
    main()
