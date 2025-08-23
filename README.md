# AI-Powered Phishing Detector with XAI

A web application that uses a machine learning model to detect phishing URLs and provides transparent, human-understandable explanations for its predictions using Explainable AI (XAI).

This project demonstrates an end-to-end MLOps pipeline, from data processing and model training to deployment as an interactive web service. The core focus is on creating a reliable and trustworthy security tool.

---
## Screenshot

Here is a preview of the application's user interface.

![Demo](https://github.com/haripatel07/xai-phishing-detector/blob/main/pictures/AI%20Phishing%20Detector.png)
---
## Features

- **High-Recall ML Model**: A `RandomForestClassifier` trained on over 500,000 URLs, specifically tuned to maximize the detection of malicious links (high recall).
- **Explainable AI (XAI)**: Integrated the **LIME** library to explain *why* a URL is flagged, showing the most influential features for each prediction. This moves the model from a "black box" to a transparent diagnostic tool.
- **Interactive Web Interface**: A clean and responsive UI built with **Flask** and modern CSS that allows for real-time URL analysis.
- **Full Data Pipeline**: Scripts for automated feature engineering, model training, and evaluation.

---
## Tech Stack

- **Backend**: Python, Flask
- **Machine Learning**: Scikit-learn, Pandas, NumPy, LIME
- **Frontend**: HTML, CSS
- **Deployment**: Local deployment via Flask's development server

---
### Dataset Information

* **Source:** [Phishing Site URLs – Kaggle](https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls)
* **Content:** The dataset contains **over 550,000 URLs**, each labeled as either **"good" (benign)** or **"bad" (malicious)**.
* **Usage:** This dataset was used to train the phishing detection model by extracting lexical and structural features from URLs.
* **Note:** Due to its large size, the dataset is **not included in this repository**.

  * To run the training pipeline, download it directly from Kaggle and place it in the `data/` directory with the name:

    ```
    phishing_data.csv
    ```

---

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

- Python 3.8+
- A virtual environment tool (`venv`)

### Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/haripatel07/xai-phishing-detector.git](https://github.com/haripatel07/xai-phishing-detector.git)
    cd xai-phishing-detector
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the data processing and model training pipeline:**
    *Note: The necessary data files are not included in this repository. Please download the dataset from [Kaggle](https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls), place `phishing_site_urls.csv` in the `data/` folder, and rename it to `phishing_data.csv`.*

    ```bash
    # Step 1: Process the raw data
    python src/features/build_features.py

    # Step 2: Train the model and generate helper files
    python src/models/train_model.py
    ```
    This will generate the `phishing_detector_model.joblib` and `training_data_sample.csv` files, which are required to run the app but are not stored in Git.

5.  **Run the Flask application:**
    ```bash
    flask run
    ```

6.  **Open your browser** and navigate to `http://127.0.0.1:5000`.

---
## Model Performance

The model was intentionally tuned to prioritize **recall for the malicious class**. This means it is optimized to minimize "false negatives" (i.e., letting a real threat go undetected). This is a critical trade-off in security applications, where a false alarm is preferable to a missed threat. The final model achieves **78% recall** on the malicious class in the test set.

---
## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
