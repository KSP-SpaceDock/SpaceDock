#!/bin/bash
set -e

# Run SpaceDock test suite
# Usage: ./run-tests.sh [--coverage] [--live]
#   --coverage: Generate coverage report
#   --live: Use the live docker database (default is to use a fresh DB)

LIVE_DB=false
COVERAGE=false

while [[ "$1" =~ ^- ]]; do
    case "$1" in
        --live) LIVE_DB=true; shift ;;
        --coverage) COVERAGE=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "Running SpaceDock tests..."
echo "Database: $([ "$LIVE_DB" = true ] && echo 'live' || echo 'fresh')"
echo "Coverage: $COVERAGE"

# If not using live DB, create a fresh database
if [ "$LIVE_DB" = false ]; then
    echo "Creating fresh test database..."
    spacedock database wait
    spacedock database initialize
    spacedock database migrate
fi

# Install test dependencies
echo "Installing test dependencies..."
pip install -r requirements-tests.txt --quiet

# Run tests
PYTEST_ARGS=""
if [ "$COVERAGE" = true ]; then
    PYTEST_ARGS="--cov=KerbalStuff --cov-report=html"
fi

pytest $PYTEST_ARGS tests/ "$@"
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✓ All tests passed"
else
    echo "✗ Some tests failed"
fi

exit $exit_code
