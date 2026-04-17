#!/bin/bash
# Simple test script that only runs what is present
echo "Running tests..."
if [ -d "tests" ] || ls test_*.py 1> /dev/null 2>&1; then pytest; fi
if [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ]; then vitest run; fi
echo "Tests complete."
