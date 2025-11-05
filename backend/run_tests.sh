#!/bin/bash
#
# Smart Research Hub - Test Runner Script
# Runs comprehensive test suite with coverage reporting
#

set -e  # Exit on error

echo "======================================"
echo "  Smart Research Hub - Test Suite"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Virtual environment not activated${NC}"
    echo "Run: source venv/bin/activate"
    echo ""
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found${NC}"
    echo "Install with: pip install -r requirements.txt"
    exit 1
fi

echo "📦 Installing/updating test dependencies..."
pip install -q pytest pytest-asyncio pytest-cov

echo ""
echo "🧪 Running test suite..."
echo ""

# Run different test suites based on argument
case "${1:-all}" in
    "unit")
        echo "Running unit tests only..."
        pytest tests/ -m unit -v
        ;;
    "integration")
        echo "Running integration tests only..."
        pytest tests/ -m integration -v
        ;;
    "fast")
        echo "Running fast tests only (excluding slow tests)..."
        pytest tests/ -m "not slow" -v
        ;;
    "coverage")
        echo "Running tests with detailed coverage report..."
        pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v
        echo ""
        echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
        ;;
    "specific")
        if [[ -z "$2" ]]; then
            echo -e "${RED}❌ Please specify test file or pattern${NC}"
            echo "Usage: ./run_tests.sh specific <pattern>"
            echo "Example: ./run_tests.sh specific test_topic_discovery_service.py"
            exit 1
        fi
        echo "Running specific tests: $2"
        pytest tests/ -k "$2" -v
        ;;
    "all"|*)
        echo "Running all tests with coverage..."
        pytest tests/ -v
        ;;
esac

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
fi

echo ""
echo "======================================"
echo "  Test Results Summary"
echo "======================================"

# Show coverage summary if coverage was generated
if [ -f ".coverage" ]; then
    echo ""
    echo "📊 Coverage Summary:"
    coverage report --skip-covered | tail -n 5
fi

echo ""
echo "Commands:"
echo "  View HTML coverage: open htmlcov/index.html"
echo "  Run specific test: ./run_tests.sh specific <pattern>"
echo "  Run fast tests: ./run_tests.sh fast"
echo "  Run unit tests: ./run_tests.sh unit"
echo ""

exit $TEST_EXIT_CODE
