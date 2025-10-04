#!/bin/bash

# PDF to YouTube Shorts - Quick Start Setup Script
# This script sets up the environment and runs a test

set -e  # Exit on error

echo "=========================================="
echo "PDF to YouTube Shorts - Quick Setup"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check FFmpeg
echo "Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n 1)
    echo -e "${GREEN}✓${NC} FFmpeg found"
else
    echo -e "${RED}✗${NC} FFmpeg not found."
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Download from ffmpeg.org"
    exit 1
fi

# Create directory structure
echo ""
echo "Creating directory structure..."
mkdir -p agents
mkdir -p temp_processing/{visuals,audio,video}
mkdir -p output_videos
mkdir -p .cache
echo -e "${GREEN}✓${NC} Directories created"

# Create virtual environment
echo ""
echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}!${NC} Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Check for API key
echo ""
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}!${NC} GEMINI_API_KEY not set in environment"
    echo "You can get a free API key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Enter your Gemini API key (or press Enter to skip): " API_KEY
    if [ ! -z "$API_KEY" ]; then
        export GEMINI_API_KEY="$API_KEY"
        echo "export GEMINI_API_KEY='$API_KEY'" >> ~/.bashrc
        echo -e "${GREEN}✓${NC} API key set"
    else
        echo -e "${YELLOW}!${NC} Skipping API key setup. You'll need to provide it when running."
    fi
else
    echo -e "${GREEN}✓${NC} GEMINI_API_KEY found in environment"
fi

# Create sample PDF if none exists
echo ""
echo "Checking for sample PDF..."
if [ ! -f "example.pdf" ]; then
    echo "Creating a sample PDF for testing..."
    python3 << EOF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("example.pdf", pagesize=letter)
c.setFont("Helvetica", 12)

# Title
c.setFont("Helvetica-Bold", 20)
c.drawString(100, 750, "The Science of Learning")

# Content
c.setFont("Helvetica", 12)
y = 700
lines = [
    "Learning is a complex cognitive process that involves multiple brain regions.",
    "",
    "Key Principles:",
    "1. Spaced Repetition: Reviewing information at increasing intervals improves retention.",
    "2. Active Recall: Testing yourself is more effective than passive reading.",
    "3. Interleaving: Mixing different topics improves long-term retention.",
    "4. Elaboration: Connecting new information to existing knowledge strengthens memory.",
    "",
    "The hippocampus plays a crucial role in forming new memories, while the",
    "prefrontal cortex is involved in working memory and decision-making.",
    "",
    "Research shows that sleep is essential for memory consolidation, with",
    "different sleep stages contributing to different types of learning.",
    "",
    "Practice and repetition create stronger neural pathways, making skills",
    "more automatic over time. This is the basis of procedural memory.",
]

for line in lines:
    c.drawString(100, y, line)
    y -= 20
    if y < 100:
        c.showPage()
        c.setFont("Helvetica", 12)
        y = 750

c.save()
EOF
    echo -e "${GREEN}✓${NC} Sample PDF created: example.pdf"
else
    echo -e "${GREEN}✓${NC} Sample PDF found: example.pdf"
fi

# Run system check
echo ""
echo "Running system check..."
python3 << EOF
import sys
sys.path.insert(0, '.')
from utils import print_system_info
print_system_info()
EOF

# Final instructions
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run a demo: python demo.py"
echo "3. Process a PDF: python main.py example.pdf --api-key YOUR_API_KEY"
echo ""
echo "For more information, see README.md"
echo ""
echo "Quick commands:"
echo "  - Test components: python demo.py (select option 5)"
echo "  - Basic conversion: python main.py example.pdf --api-key \$GEMINI_API_KEY"
echo "  - View help: python main.py --help"
echo ""

# Offer to run a test
read -p "Would you like to run a component test now? (y/n): " RUN_TEST
if [ "$RUN_TEST" = "y" ] || [ "$RUN_TEST" = "Y" ]; then
    echo ""
    echo "Running component tests..."
    python3 -c "from demo import demo_test_components; demo_test_components()"
fi

echo ""
echo -e "${GREEN}All done! Happy creating! 🎬${NC}"