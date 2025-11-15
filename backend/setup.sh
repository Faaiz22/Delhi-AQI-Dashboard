#!/bin/bash

echo "🚀 Delhi AQI Dashboard - AI Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install streamlit pandas numpy requests pydeck plotly geopandas shapely pyproj pykrige scipy google-generativeai python-dotenv

echo ""
echo "✅ All dependencies installed successfully!"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Google Gemini API Key
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY="AIzaSyAqrq5wpkdhg9L2dMQwmhr8YULz7HYKGIs"

# Gmail Settings for SMS (optional)
SENDER_EMAIL=anumaliknr@gmail.com
GMAIL_APP_PASSWORD=your-app-password
EOF
    echo "✅ .env file created. Please edit it with your API keys."
else
    echo "✅ .env file already exists"
fi

# Check for .streamlit/secrets.toml
if [ ! -f .streamlit/secrets.toml ]; then
    echo "📝 Creating Streamlit secrets file..."
    mkdir -p .streamlit
    cat > .streamlit/secrets.toml << EOF
# Google Gemini API Key
GEMINI_API_KEY = "AIzaSyAqrq5wpkdhg9L2dMQwmhr8YULz7HYKGIs"

# Gmail Settings for SMS (optional)
SENDER_EMAIL = "anumaliknr@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"
EOF
    echo "✅ Streamlit secrets file created"
else
    echo "✅ Streamlit secrets file already exists"
fi

echo ""
echo "=========================================="
echo "🎉 Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env or .streamlit/secrets.toml with your Gemini API key"
echo "   Get your key from: https://makersuite.google.com/app/apikey"
echo ""
echo "2. Run the application:"
echo "   streamlit run backend/app.py"
echo ""
echo "3. Optional: Set up Gmail App Password for SMS alerts"
echo "   Guide: https://support.google.com/accounts/answer/185833"
echo ""
echo "=========================================="
