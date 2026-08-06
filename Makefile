PYTHON    := python3
MAIN      := n_puzzle.py
# Same program as MAIN, reached as a module so pdb starts inside the solver
# instead of stopping on the launcher's import line.
DEBUG_MAIN := npuzzle.main
# Verifies the sequence MAIN printed really solves the puzzle.
# CHECKER   := tests/test_solution.py (old version, now replaced by checker.py)
CHECKER   := tests/checker.py
# Arguments forwarded to the solver, e.g. make run ARGS="-r 4 -hf linear".
ARGS      ?=
# Board `make test` solves before checking the printed sequence is legal.
TESTBOARD ?= tests/3x3_solvable
TESTOUT   := .test_output
# A bare `make` lists the rules rather than running the first one by accident.
.DEFAULT_GOAL := help

help:
	@echo 'Usage: make <rule> [ARGS="<solver flags>"]'
	@echo
	@echo '  install  report dependencies (none, standard library only)'
	@echo '  run      solve a puzzle'
	@echo '  debug    solve a puzzle under pdb'
	@echo '  test     solve TESTBOARD, then verify the printed sequence'
	@echo '  clean    remove caches and generated output'
	@echo '  help     show this message'
	@echo
	@echo 'Solver flags: [board] [-r <size>] [-hf <heuristic>]'
	@echo '              [-av <variant>] [-gs <goal_state>] [-t]'
	@echo 'Examples:'
	@echo '  make run ARGS="tests/4x4_solvable -hf linear -t"'
	@echo '  make run ARGS="-r 3 -av greedy -gs top_left"'
	@echo '  make test TESTBOARD=tests/4x4_solvable'
	@echo
	@echo 'Run "make run ARGS=-h" for the full solver help.'

# Nothing to fetch: the solver imports only the standard library.
install:
	@echo "No dependencies to install - $(MAIN) uses the standard library only."

run:
	$(PYTHON) $(MAIN) $(ARGS)

debug:
	$(PYTHON) -m pdb -m $(DEBUG_MAIN) $(ARGS)

# Solve TESTBOARD, then hand the output to the checker, which re-reads the
# printed sequence and confirms every step is a single legal slide ending on
# the declared goal. The output file is kept only for the length of the run.
test:
	@$(PYTHON) $(MAIN) $(TESTBOARD) > $(TESTOUT)
	@$(PYTHON) $(CHECKER) $(TESTOUT)
	@rm -f $(TESTOUT)

# Caches and generated output only; board files and tests are left alone.
clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache $(TESTOUT)
	find . -name '*.pyc' -delete

.PHONY: help install run debug test clean
