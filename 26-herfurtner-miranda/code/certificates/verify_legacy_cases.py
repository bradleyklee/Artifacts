#!/usr/bin/env python3
"""Backward-compatible wrapper for models 1, 2, 3, and 9."""
from verify_complete_cases import main

MODEL_SUBSET = (1, 2, 3, 9)

if __name__ == "__main__":
    main(default_models=MODEL_SUBSET)
