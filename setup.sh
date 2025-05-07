#!/bin/bash
#
# TopCV Job Crawler Setup Script
#
# This script sets up the environment for the TopCV job crawler.
# It checks for required dependencies, creates a virtual environment,
# and installs the required packages.
#

set -e  # Exit on error

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print with color
print_green() { echo -e "${GREEN}$1${NC}"; }
print_yellow() { echo -e "${YELLOW}$1${NC}"; }
print_red() { echo -e "${RED}$1${NC}"; }
print_blue() { echo -e "${BLUE}$1${NC}"; }

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if Docker should be used
use_docker=false
build_docker=false

# Process command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            use_docker=true
            shift
            ;;
        --build-docker)
            use_docker=true
            build_docker=true
            shift
            ;;
        *)
            print_red "Unknown option: $1"
            echo "Usage: $0 [--docker] [--build-docker]"
            exit 1
            ;;
    esac
done

print_blue "╔════════════════════════════════════════════╗"
print_blue "║      TopCV Job Crawler - Setup Script      ║" 
print_blue "╚════════════════════════════════════════════╝"
echo

# If using Docker
if $use_docker; then
    print_blue "🐳 Docker mode selected"
    
    # Check if Docker is installed
    if ! command_exists docker; then
        print_red "❌ Docker is not installed. Please install Docker and try again."
        exit 1
    fi
    
    print_green "✅ Docker is installed"
    
    # Build Docker image if requested
    if $build_docker; then
        print_blue "🔨 Building Docker image..."
        docker build -t topcv-job-crawler .
        print_green "✅ Docker image built successfully"
    fi
    
    print_blue "🚀 Running Docker container..."
    echo "The container will run in the background with data and logs volumes mounted."
    echo "To see logs, run: docker logs -f topcv-job-crawler"
    
    # Create directories if they don't exist
    mkdir -p data logs
    
    # Run Docker container
    docker run -d --name topcv-job-crawler \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        topcv-job-crawler
    
    print_green "✅ Docker container started successfully"
    exit 0
fi

# Check for Python
print_blue "🔍 Checking for Python..."
if ! command_exists python3; then
    print_red "❌ Python 3 not found. Please install Python 3.7 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 --version | awk '{print $2}')
print_green "✅ Found Python $python_version"

# Check major.minor version
python_major_minor=$(echo $python_version | cut -d. -f1,2)
if (( $(echo "$python_major_minor < 3.7" | bc -l) )); then
    print_red "❌ Python version too old. Please install Python 3.7 or higher."
    exit 1
fi

# Check for pip
print_blue "🔍 Checking for pip..."
if ! command_exists pip3; then
    print_red "❌ pip3 not found. Please install pip for Python 3."
    exit 1
fi
print_green "✅ pip3 is installed"

# Check for virtualenv module
print_blue "🔍 Checking for venv module..."
if ! python3 -m venv --help &> /dev/null; then
    print_yellow "⚠️ Python venv module not found. Attempting to install..."
    
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y python3-venv
    elif command_exists brew; then
        brew install python3
    else
        print_red "❌ Cannot install venv module automatically. Please install it manually."
        exit 1
    fi
fi
print_green "✅ venv module is available"

# Create virtual environment
print_blue "🔧 Creating virtual environment..."
python3 -m venv venv
print_green "✅ Virtual environment created"

# Activate virtual environment
print_blue "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if activation worked
if [ "$VIRTUAL_ENV" = "" ]; then
    print_red "❌ Failed to activate virtual environment."
    exit 1
fi
print_green "✅ Virtual environment activated"

# Install dependencies
print_blue "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_green "✅ Dependencies installed successfully"

# Create necessary directories
print_blue "📁 Creating data and logs directories..."
mkdir -p data logs
print_green "✅ Directories created"

# Setup complete
print_blue "╔════════════════════════════════════════════╗"
print_blue "║             Setup completed!               ║"
print_blue "╚════════════════════════════════════════════╝"
echo
print_yellow "To activate the virtual environment manually in the future, run:"
echo "  source venv/bin/activate"
echo
print_yellow "To start the crawler, run:"
echo "  python crawler.py"
echo
print_yellow "For more options, run:"
echo "  python crawler.py --help"
echo
print_green "Happy job crawling! 🚀" 