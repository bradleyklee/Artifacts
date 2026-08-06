#!/usr/bin/env python3
"""Backward-compatible wrapper for models 5 and 7."""
from verify_complete_cases import main

MODEL_SUBSET = (5, 7)

if __name__ == "__main__":
    main(default_models=MODEL_SUBSET)
