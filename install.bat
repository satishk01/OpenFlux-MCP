@echo off
REM OpenFlux Installation Script for Windows
REM This script sets up OpenFlux on a Windows system

echo 🚀 Starting OpenFlux installation...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo ✅ pip found

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

echo ✅ Python dependencies installed

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ uv package manager not found
    echo Installing uv for MCP server support...
    
    REM Install uv using pip as fallback for Windows
    pip install uv
    if errorlevel 1 (
        echo ❌ Failed to install uv
        echo Please install uv manually: https://docs.astral.sh/uv/getting-started/installation/
        pause
        exit /b 1
    )
)

echo ✅ uv package manager available

REM Create .env file if it doesn't exist
if not exist .env (
    echo ⚙️ Creating .env file from template...
    copy .env.example .env
    echo ✅ .env file created
    echo ⚠️ Please edit .env file with your configuration:
    echo   - Set GITHUB_TOKEN
    echo   - Configure AWS credentials
    echo   - Adjust AWS_REGION if needed
) else (
    echo ✅ .env file already exists
)

REM Run tests
echo 🧪 Running application tests...
python test_app.py
if errorlevel 1 (
    echo ⚠️ Some tests failed, but installation completed
    echo Please check the test output above
) else (
    echo ✅ All tests passed!
)

echo.
echo 🎉 OpenFlux installation completed!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your configuration
echo 2. Configure AWS credentials (aws configure or set environment variables)
echo 3. Set your GitHub token in the .env file
echo 4. Run the application: streamlit run app.py
echo.
echo 🔧 Useful commands:
echo - Test installation: python test_app.py
echo - Start application: streamlit run app.py
echo - View help: streamlit run app.py --help
echo.

pause