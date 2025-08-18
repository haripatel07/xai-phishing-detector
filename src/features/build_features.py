import pandas as pd
from urllib.parse import urlparse
import re

def extract_features(url):
    """
    Extracts various lexical features from a URL.
    
    Args:
        url (str): The URL to process.
        
    Returns:
        dict: A dictionary of extracted features.
    """
    features = {}
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
    except (ValueError, TypeError):
        # Handle cases where URL is not a string or is malformed
        parsed_url = None
        domain = ''
        url = str(url) # Ensure url is a string

    # 1. Length-based features
    features['url_length'] = len(url)
    features['domain_length'] = len(domain)

    # 2. Special character counts
    features['qty_dots'] = url.count('.')
    features['qty_hyphens'] = url.count('-')
    features['qty_at'] = url.count('@')
    features['qty_question'] = url.count('?')
    features['qty_and'] = url.count('&')
    features['qty_or'] = url.count('|')
    features['qty_equal'] = url.count('=')
    features['qty_underscore'] = url.count('_')
    features['qty_tilde'] = url.count('~')
    features['qty_percent'] = url.count('%')
    features['qty_slash'] = url.count('/')
    features['qty_star'] = url.count('*')
    features['qty_colon'] = url.count(':')
    features['qty_comma'] = url.count(',')
    features['qty_semicolon'] = url.count(';')
    features['qty_dollar'] = url.count('$')
    features['qty_space'] = url.count(' ')

    # 3. Keyword-based features (presence of sensitive words)
    sensitive_words = ['secure', 'login', 'signin', 'bank', 'account', 'password']
    features['sensitive_words'] = sum([url.lower().count(word) for word in sensitive_words])

    # 4. Domain-based features
    features['is_ip'] = 1 if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain) else 0
    features['has_https'] = 1 if parsed_url and parsed_url.scheme == 'https' else 0

    return features

def main():
    """
    Main function to load data, process it, and save the features.
    """
    print("Starting feature extraction...")
    
    # Load the raw dataset
    try:
        df = pd.read_csv('data/phishing_data.csv')
    except FileNotFoundError:
        print("Error: 'data/phishing_data.csv' not found. Make sure you've downloaded the dataset and renamed it.")
        return

    # Drop any rows with missing URLs
    df.dropna(subset=['URL'], inplace=True)
    
    # Rename columns from the dataset to match what our code expects ('url' and 'type')
    df.rename(columns={'URL': 'url', 'Label': 'type'}, inplace=True)

    # Extract features for each URL
    features_list = df['url'].apply(extract_features)
    features_df = pd.DataFrame(features_list.tolist())

    # Combine original data with new features
    processed_df = pd.concat([df.drop('url', axis=1).reset_index(drop=True), features_df.reset_index(drop=True)], axis=1)

    # Map 'good' to 0 and 'bad' to 1 for the model
    label_mapping = {'good': 0, 'bad': 1}
    processed_df['label'] = processed_df['type'].map(label_mapping)

    # Drop the original 'type' column and any rows that couldn't be mapped
    processed_df = processed_df.drop('type', axis=1)
    processed_df.dropna(subset=['label'], inplace=True)

    # Save the processed data
    processed_df.to_csv('data/processed_data.csv', index=False)
    
    print(f"Feature extraction complete. Processed {len(processed_df)} URLs.")
    print("Processed data saved to 'data/processed_data.csv'")

if __name__ == "__main__":
    main()