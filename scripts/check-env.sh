#!/usr/bin/env bash
# Environment check for math-trace
# Detects missing dependencies and provides install instructions per OS

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

echo -e "${BOLD}🔍 Checking math-trace environment...${RESET}\n"

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)

# Check if command exists
has_cmd() {
    command -v "$1" &> /dev/null
}

# Track failures
MISSING=()

# Check Python
echo -n "Python 3.13: "
if has_cmd python3; then
    PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ "$PY_VERSION" == "3.13" ]]; then
        echo -e "${GREEN}✓${RESET} (${PY_VERSION})"
    else
        echo -e "${RED}✗${RESET} (found ${PY_VERSION}, need 3.13)"
        MISSING+=("python3")
    fi
else
    echo -e "${RED}✗${RESET} (not found)"
    MISSING+=("python3")
fi

# Check uv
echo -n "uv (Python package manager): "
if has_cmd uv; then
    UV_VERSION=$(uv --version 2>/dev/null | awk '{print $2}')
    echo -e "${GREEN}✓${RESET} (${UV_VERSION})"
else
    echo -e "${YELLOW}⚠${RESET}  (not found, will install)"
    MISSING+=("uv")
fi

# Check Typst
echo -n "Typst (PDF compiler): "
if has_cmd typst; then
    TYPST_VERSION=$(typst --version)
    echo -e "${GREEN}✓${RESET} (${TYPST_VERSION})"
else
    echo -e "${YELLOW}⚠${RESET}  (not found, required for PDF generation)"
    MISSING+=("typst")
fi

# Check git
echo -n "git: "
if has_cmd git; then
    echo -e "${GREEN}✓${RESET}"
else
    echo -e "${RED}✗${RESET} (not found)"
    MISSING+=("git")
fi

echo ""

# Report findings
if [ ${#MISSING[@]} -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✅ All dependencies found!${RESET}"
    echo "Ready to run: ${BOLD}just paper${RESET}"
    exit 0
fi

echo -e "${YELLOW}${BOLD}📦 Missing dependencies:${RESET}"
for dep in "${MISSING[@]}"; do
    echo "  • $dep"
done

echo ""
echo -e "${BOLD}Installation instructions for $OS:${RESET}\n"

if [[ "$OS" == "macos" ]]; then
    if [[ " ${MISSING[@]} " =~ " python3 " ]]; then
        echo "  ${BOLD}Python 3.13:${RESET}"
        echo "    brew install python@3.13"
        echo ""
    fi

    if [[ " ${MISSING[@]} " =~ " uv " ]]; then
        echo "  ${BOLD}uv (package manager):${RESET}"
        echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "    # Then add to ~/.zshrc or ~/.bash_profile:"
        echo "    export PATH=\"\$HOME/.cargo/bin:\$PATH\""
        echo ""
    fi

    if [[ " ${MISSING[@]} " =~ " typst " ]]; then
        echo "  ${BOLD}Typst (recommended - official installer):${RESET}"
        echo "    curl -fsSL https://install.typst.community/install.sh | sh"
        echo "    # Then add to ~/.zshrc or ~/.bash_profile:"
        echo "    export PATH=\"\$HOME/.typst/bin:\$PATH\""
        echo ""
        echo "  Or via Homebrew:"
        echo "    brew install typst"
        echo ""
    fi

elif [[ "$OS" == "linux" ]]; then
    if [[ " ${MISSING[@]} " =~ " python3 " ]]; then
        echo "  ${BOLD}Python 3.13:${RESET}"
        echo "    # Ubuntu/Debian:"
        echo "    sudo apt-get update && sudo apt-get install -y python3.13"
        echo "    # Fedora:"
        echo "    sudo dnf install -y python3.13"
        echo ""
    fi

    if [[ " ${MISSING[@]} " =~ " uv " ]]; then
        echo "  ${BOLD}uv (package manager):${RESET}"
        echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "    # Then add to ~/.bashrc:"
        echo "    export PATH=\"\$HOME/.cargo/bin:\$PATH\""
        echo ""
    fi

    if [[ " ${MISSING[@]} " =~ " typst " ]]; then
        echo "  ${BOLD}Typst (recommended - official installer):${RESET}"
        echo "    curl -fsSL https://install.typst.community/install.sh | sh"
        echo "    # Then add to ~/.bashrc:"
        echo "    export PATH=\"\$HOME/.typst/bin:\$PATH\""
        echo ""
        echo "  Or via package manager:"
        echo "    # Ubuntu/Debian:"
        echo "    sudo apt-get install -y typst"
        echo "    # Fedora:"
        echo "    sudo dnf install -y typst"
        echo ""
    fi

elif [[ "$OS" == "windows" ]]; then
    echo "  ${BOLD}Windows (WSL2 recommended):${RESET}"
    echo "  math-trace works best on WSL2 (Windows Subsystem for Linux)."
    echo ""
    echo "  ${BOLD}1. Enable WSL2:${RESET}"
    echo "    wsl --install"
    echo ""
    echo "  ${BOLD}2. Once in WSL2, follow Linux instructions above${RESET}"
    echo ""
    echo "  Alternatively, install native versions:"
    echo ""

    if [[ " ${MISSING[@]} " =~ " python3 " ]]; then
        echo "  ${BOLD}Python 3.13:${RESET}"
        echo "    Visit https://www.python.org/downloads/"
        echo "    Download Python 3.13 installer and run (enable 'Add Python to PATH')"
        echo ""
    fi

    if [[ " ${MISSING[@]} " =~ " uv " ]]; then
        echo "  ${BOLD}uv (package manager):${RESET}"
        echo "    https://github.com/astral-sh/uv/releases"
        echo "    Download uv-x86_64-pc-windows-gnu.zip, extract, add to PATH"
        echo ""
    fi

    if [[ " ${MISSING[@]} " =~ " typst " ]]; then
        echo "  ${BOLD}Typst:${RESET}"
        echo "    https://github.com/typst/typst/releases"
        echo "    Download typst-x86_64-pc-windows-msvc.zip, extract, add to PATH"
        echo ""
    fi
else
    echo "  ${YELLOW}Unknown OS. Please refer to:${RESET}"
    echo "    Python: https://www.python.org/"
    echo "    uv: https://github.com/astral-sh/uv"
    echo "    Typst: https://typst.app/docs/installation/"
fi

echo -e "${BOLD}After installing, run:${RESET}"
echo "  source ~/.bashrc  # or ~/.zshrc for macOS"
echo "  ${BOLD}just setup${RESET}"
echo ""

exit 1
