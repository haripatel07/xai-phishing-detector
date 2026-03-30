import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

def main():
    """
    Main function to train, evaluate, and save the model and a data sample.
    """
    print("Starting model training...")

    # Load the processed data
    try:
        df = pd.read_csv('data/processed_data.csv')
    except FileNotFoundError:
        print("Error: 'data/processed_data.csv' not found. Please run the feature extraction script first.")
        return

    df.dropna(inplace=True)

    # Separate features (X) and the target label (y)
    X = df.drop('label', axis=1)
    y = df['label']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Data split into {len(X_train)} training samples and {len(X_test)} testing samples.")

    # Initialize and train the Random Forest Classifier
    print("Training the Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')
    model.fit(X_train, y_train)

    # Make predictions on the test set
    print("Evaluating the model...")
    y_pred = model.predict(X_test)

    # Evaluate the model's performance
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=['Benign (0)', 'Malicious (1)'])

    print(f"\nModel Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(report)

    # We can't save the LIME explainer directly, so we save a sample of the training data instead.
    print("\nSaving a sample of the training data for the explainer...")
    X_train_sample = X_train.sample(n=500, random_state=42)
    sample_path = 'data/training_data_sample.csv'
    X_train_sample.to_csv(sample_path, index=False)
    print(f"Training data sample saved to '{sample_path}'")

    # Save the trained model
    model_path = 'models/phishing_detector_model.joblib'
    joblib.dump(model, model_path)
    print(f"\nModel saved successfully to '{model_path}'")

if __name__ == "__main__":
    main()