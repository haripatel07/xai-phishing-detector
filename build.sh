#!/bin/bash

# Exit if any command fails
set -e

# Install Python dependencies
pip install -r requirements.txt

# Download the dataset
echo "Downloading dataset..."
mkdir -p data
curl -L -o data/phishing_data.csv "https://media.githubusercontent.com/media/shashwatwork/Phishing-Site-URLs/main/phishing_site_urls.csv"

# Run the data processing and model training scripts
echo "Processing data and training model..."
python src/features/build_features.py
python src/models/train_model.py

echo "Build complete!"