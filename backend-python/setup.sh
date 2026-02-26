# setup.sh
#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy example env file
cp .env.example .env

echo "Setup complete! Please:"
echo "1. Update .env with your OpenRouter API key"
echo "2. Place your lama1.pdf file in the project root"
echo "3. Run: python run.py"