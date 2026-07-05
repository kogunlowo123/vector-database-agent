#!/bin/bash
set -euo pipefail
echo "Setting up Vector Database Agent..."
pip install -e ".[dev]"
echo "Setup complete!"
