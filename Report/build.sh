#!/usr/bin/env bash
# Build the Cairo formal report PDF.
# Run twice so the table of contents resolves.
set -e

cd "$(dirname "$0")"

echo "==> First xelatex pass"
xelatex -interaction=nonstopmode -shell-escape main.tex

echo "==> Second xelatex pass (ToC resolution)"
xelatex -interaction=nonstopmode -shell-escape main.tex

echo "==> Done.  Output: Report/main.pdf"
