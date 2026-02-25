#!/bin/bash
# DuckDuckGo Search Wrapper for OpenClaw
# Usage: ddg-search.sh "your search query"

set -e

# Default settings
RESULTS=10
USE_LITE=false
USE_NEWS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--number)
            RESULTS="$2"
            shift 2
            ;;
        -l|--lite)
            USE_LITE=true
            shift
            ;;
        --news)
            USE_NEWS=true
            shift
            ;;
        -h|--help)
            echo "DuckDuckGo Search Wrapper"
            echo ""
            echo "Usage: ddg-search.sh [options] <query>"
            echo ""
            echo "Options:"
            echo "  -n, --number NUM     Show NUM results (default: 10)"
            echo "  -l, --lite           Use lite version"
            echo "  --news               Search news only"
            echo "  -h, --help           Show this help"
            echo ""
            echo "Examples:"
            echo "  ddg-search.sh 'Python programming tutorial'"
            echo "  ddg-search.sh -n 5 'latest AI news'"
            echo "  ddg-search.sh -l 'weather forecast'"
            exit 0
            ;;
        *)
            # Rest is the search query
            QUERY="$@"
            shift $#
            ;;
    esac
done

# Check if query is provided
if [ -z "$QUERY" ]; then
    echo "Error: No search query provided"
    echo "Use: ddg-search.sh 'your query' or -h for help"
    exit 1
fi

# Build ddgr command
CMD="ddgr"
CMD="$CMD -x"  # Exit after results
CMD="$CMD -n $RESULTS"  # Number of results
[ "$USE_NEWS" = true ] && CMD="$CMD --np --d 0d"  # No prompt + time limit 0 days for news
CMD="$CMD \"$QUERY\""

# Execute search
eval "$CMD"
