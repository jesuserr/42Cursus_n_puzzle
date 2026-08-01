#!/usr/bin/env python3
# Entry point. The solver lives in the npuzzle package; this only forwards to
# it, so `python3 n_puzzle.py [board] [options]` keeps working unchanged.
from npuzzle.main import main

if __name__ == "__main__":
    main()
