#!/usr/bin/env bash
set -euo pipefail

# Demo: use kernel_sim non-interactively to create and show a file
KERN=../kernel_sim

printf "write demo.txt This_is_a_demo_from_script\nls\ncat demo.txt\nexit\n" | "$KERN"
