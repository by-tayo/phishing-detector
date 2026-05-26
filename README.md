# 🛡️ AI-Powered Phishing URL Detector

## 📌 Overview

This project builds a **full-stack AI-powered phishing detection system** that classifies URLs as phishing or legitimate in real time.
The pipeline:

* Downloads and preprocesses phishing URLs from **PhishTank** and legitimate URLs from **Majestic Million**.
* Trains **three ML models** — Logistic Regression, Random Forest, and XGBoost — using TF-IDF character n-gram features.
* Fine-tunes a **DistilBERT transformer** model for deep contextual URL understanding.
* Exposes predictions via a **FastAPI REST API** with three endpoints.
* Displays results in an interactive **Plotly Dash frontend** with red/green result cards.
* Provisions cloud infrastructure on **AWS** using **Terraform**.

---

## 📑 Table of Contents

1. [Project Objectives](#-project-objectives)
2. [Project Structure](#-project-structure)
3. [Dataset](#-dataset)
4. [ML Models & Results](#-ml-models--results)
5. [API Endpoints](#-api-endpoints)
6. [Frontend](#-frontend)
7. [AWS Infrastructure](#-aws-infrastructure)
8. [How to Run](#-how-to-run)
9. [Tools and Libraries](#-tools-and-libraries)
10. [Example Predictions](#-example-predictions)
11. [Security Notes](#-security-notes)
12. [Possible Extensions](#-possible-extensions)

---

## 🎯 Project Objectives

* Build a real-time phishing URL classifier using multiple AI approaches.
* Engineer character-level TF-IDF features that capture phishing URL patterns.
* Fine-tune a pre-trained DistilBERT transformer on a balanced phishing dataset.
* Expose predictions through a documented REST API built with FastAPI.
* Build an interactive frontend dashboard using Plotly Dash.
* Provision reproducible cloud infrastructure on AWS using Terraform IaC.
* Integrate a live threat feed (OpenPhish) for real-time phishing verification.

---

## 📂 Project Structure

*(Note: Large datasets, `.csv` files, heavy model weights, and local `.terraform` states are explicitly `.gitignored` to keep the repository lightweight.)*

```text
phishing-detector/
├── backend/
│   ├── infra/                       # Terraform AWS configuration
│   │   ├── .terraform.lock.hcl      # Terraform dependency lock
│   │   ├── main.tf                  # Core AWS resource definitions
│   │   ├── outputs.tf               # Resource URLs and identifiers
│   │   ├── provider.tf              # AWS provider configuration
│   │   └── variables.tf             # Input variables
│   ├── main.py                      # FastAPI application
│   ├── model.py                     # Backend ML model loader
│   ├── requirements.txt             # Backend dependencies
│   └── schemas.py                   # Request/response schemas
├── ml/
│   ├── data/
│   │   ├── build_dataset.py         # Dataset construction script
│   │   └── combine_dataset.py       # Dataset merging script (generates local CSVs)
│   ├── models/
│   │   └── phishing-bert/           # DistilBERT configuration files
│   │       ├── config.json
│   │       ├── tokenizer.json
│   │       └── tokenizer_config.json
│   ├── my_dash_app_frontend/        # Plotly Dash frontend application
│   │   ├── app.py                   # Frontend main application
│   │   └── assets/
│   │       └── style.css            # Custom CSS styling
│   ├── evaluate.py                  # Scikit-learn model evaluation
│   ├── evaluate_transformer.py      # Transformer model evaluation
│   ├── fine_tune.py                 # DistilBERT fine-tuning script
│   ├── model.py                     # ML model architecture/definitions
│   ├── phishing_model.pkl           # Saved Random Forest model
│   ├── phishing_model_xgb.pkl       # Saved XGBoost model
│   ├── phishtank_api.py             # OpenPhish live feed integration
│   ├── predict.py                   # ML model inference
│   ├── predict_transformer.py       # Transformer inference
│   ├── preprocess.py                # TF-IDF preprocessing pipeline
│   ├── preprocess_phishtank.py      # PhishTank data cleaning script
│   ├── tokenize_data.py             # Hugging Face tokenization
│   ├── train.py                     # Model training (LR, RF, XGBoost)
│   └── vectorizer.pkl               # Saved TF-IDF vectorizer
├── confusion_matrix.png             # ML model evaluation plot
├── confusion_matrix_bert.png        # BERT evaluation plot
├── Dockerfile                       # Docker container configuration
├── dockerignore                     # Docker ignore rules
├── .gitignore                       # Git ignore rules
└── README.md
```

---

## 📊 Dataset

### Phishing URLs — PhishTank
* Source: [PhishTank](http://data.phishtank.com/data/online-valid.csv) — operated by Cisco Talos Intelligence Group.
* Filtered to verified phishing entries only (`verified == 'yes'`).
* Key columns used: `url`, `verified`, `target`.
* **55,877 verified phishing URLs** after preprocessing.

### Legitimate URLs — Majestic Million
* Source: [Majestic Million](https://majestic.com/reports/majestic-million) — top 1 million most-visited domains.
* Formatted as `https://www.[domain]` and labeled as legitimate.
* **55,877 legitimate URLs sampled** to match phishing count.

### Combined Dataset
* **111,754 total URLs** — perfectly balanced (50/50 split).
* Labels: `1 = phishing`, `0 = legitimate`.
* Saved to `ml/data/final_dataset.csv`.

---

## 🤖 ML Models & Results

### Feature Engineering — TF-IDF
URL text was converted to numerical features using TF-IDF with character n-grams:

* `max_features`: 5,000
* `analyzer`: `char_wb` (character-level within word boundaries)
* `ngram_range`: `(2, 4)` — captures patterns like `login`, `verify`, `secure`

### Scikit-learn + XGBoost Models

| Model | Accuracy | Precision | Recall | F1 Score |
|-------|----------|-----------|--------|----------|
| Logistic Regression | ~99% | ~99% | ~99% | ~99% |
| Random Forest | 99.92% | 99.98% | 99.87% | 99.92% |
| XGBoost | 99.92% | 99.98% | 99.87% | 99.92% |

XGBoost validation log-loss dropped from `0.599` at round 0 to `0.015` by round 50, stabilizing at `0.014` at completion.

### DistilBERT Transformer (Fine-tuned on Google Colab T4 GPU)

| Epoch | Training Loss | Validation Loss | Accuracy | F1 Score |
|-------|--------------|-----------------|----------|----------|
| 1 | 0.004179 | 0.020120 | 99.75% | 99.75% |
| 2 | 0.003817 | 0.003067 | 99.96% | 99.96% |
| 3 | 0.001172 | 0.002017 | **99.98%** | **99.98%** |

The fine-tuned model achieved **perfect 100% accuracy** on a 500-sample evaluation with zero false positives and zero false negatives.

### Saved Model Artifacts

* `ml/phishing_model.pkl` — Random Forest model (4.15 MB)
* `ml/phishing_model_xgb.pkl` — XGBoost model (282 KB)
* `ml/vectorizer.pkl` — TF-IDF vectorizer (165 KB)
* `ml/models/phishing-bert/` — Fine-tuned DistilBERT model folder

---

## 🔌 API Endpoints

The FastAPI backend exposes three prediction endpoints:

### `POST /predict`
XGBoost / Random Forest ML model prediction.

```json
// Request
{ "text": "http://suspicious-login.verify-account.com" }

// Response
{ "input": "http://suspicious-login.verify-account.com", "is_phishing": true, "confidence": 1.0 }
```

### `POST /predict/transformer`
Fine-tuned DistilBERT transformer prediction.

```json
// Request
{ "text": "https://www.google.com" }

// Response
{ "input": "https://www.google.com", "is_phishing": false, "confidence": 0.9999 }
```

### `POST /check-live`
Real-time OpenPhish live threat database lookup.

```json
// Request
{ "text": "http://suspicious-login.com" }

// Response
{ "url": "http://suspicious-login.com", "in_database": false, "verified": false, "source": "OpenPhish" }
```

Interactive API documentation is auto-generated by FastAPI.

---

## 🖥️ Frontend

The Plotly Dash frontend (`my_dash_app/app.py`) provides:

* **URL input field** — enter any URL to check
* **Model selector dropdown** — choose between XGBoost, DistilBERT, or Live Check
* **⚠️ Red card** — displayed for phishing URLs with confidence percentage
* **✅ Green card** — displayed for legitimate URLs with confidence percentage
* **Loading spinner** — shown while waiting for API response
* **How it works section** — explains all three detection methods

---

## ☁️ AWS Infrastructure

All AWS resources were provisioned using **Terraform** (Infrastructure as Code):

| AWS Resource | Details |
|-------------|---------|
| IAM Role | Permissions and access management |
| VPC | Isolated network |
| S3 Bucket | ML model artifact and log storage |
| RDS MySQL 8.0 | Phishing scan history database (`db.t3.micro`, 20 GB) |

### Terraform Commands

```bash
cd backend/infra
terraform init      # Initialize providers
terraform plan      # Preview changes
terraform apply     # Deploy infrastructure
terraform destroy   # Tear down infrastructure
```

---

## ⚙️ How to Run

### Prerequisites
* Python 3.12+
* Cursor IDE
* WSL (Ubuntu) or Linux
* AWS CLI configured (`aws configure`)
* Terraform installed

### 1. Activate virtual environment
```bash
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Build the dataset
```bash
python3 ml/preprocess_phishtank.py
python3 ml/data/combine_dataset.py
```

### 4. Train the models
```bash
python3 ml/train.py
```

### 5. Start the FastAPI backend
```bash
cd backend
uvicorn main:app --reload
```

* API: `http://localhost:8000`
* Swagger docs: `http://localhost:8000/docs`

### 6. Start the Dash frontend
Open a new terminal:
```bash
python3 my_dash_app/app.py
```

* Dashboard: `http://localhost:8050`

---

## 🛠 Tools and Libraries

* **Python 3.12** — core language
* **Scikit-learn** — Logistic Regression, Random Forest, TF-IDF, evaluation metrics
* **XGBoost** — gradient boosting classifier
* **Hugging Face Transformers** — DistilBERT fine-tuning and inference
* **PyTorch** — deep learning backend for transformer training
* **FastAPI** — REST API framework
* **Uvicorn** — ASGI server
* **Plotly Dash** — interactive frontend dashboard
* **Dash Bootstrap Components** — UI styling
* **Pandas / NumPy** — data processing
* **Matplotlib / Seaborn** — confusion matrix and evaluation plots
* **Joblib** — model serialization
* **Requests** — HTTP calls to OpenPhish
* **Terraform** — AWS infrastructure as code
* **AWS CLI** — cloud credential management
* **Google Colab** — GPU training for DistilBERT (T4 GPU)
* **Cursor IDE** — development environment
* **WSL (Ubuntu)** — Linux environment on Windows

---

## 🧪 Example Predictions

| URL | Result | Confidence |
|-----|--------|-----------|
| `http://suspicious-login.verify-account.com` | ⚠️ Phishing | 100.00% |
| `http://secure-login.verify-account.phishing.com` | ⚠️ Phishing | 100.00% |
| `https://www.google.com` | ✅ Safe | 99.99% |
| `https://www.amazon.com` | ✅ Safe | 100.00% |
| `https://www.github.com` | ✅ Safe | 100.00% |

---

## 🔒 Security Notes

* Never commit `.env` or `terraform.tfvars` to version control — both are in `.gitignore`.
* Database password stored only in `terraform.tfvars` (gitignored).
* API keys stored as environment variables, never in source code.

---

## 🚀 Possible Extensions

* **Full-Body Phishing Email Dataset Integration:** Expand the data pipeline to ingest email text headers and body text datasets (e.g., the Enron or Nazario phishing corpuses). This will allow the system to transition from a pure URL classifier to a multi-modal security platform analyzing both links and textual email context simultaneously.
* **Production Deployment via Heroku or AWS App Runner:** Containerize the entire stack using the root `Dockerfile` to host the FastAPI backend and Dash frontend on a production-grade platform like Heroku or AWS App Runner for high availability and public access.
* **SSL/TLS Certificate Implementation:** Provision a verified SSL/TLS certificate via Let's Encrypt (using Certbot) or AWS Certificate Manager (ACM) to transition the live platform from `http://` to `https://`. This guarantees secure, encrypted traffic for all incoming API queries and user dashboard interactions.
* **Relational Database Logging:** Fully integrate the provisioned AWS RDS MySQL database instance to log a persistent history of scan transactions, allowing the system to populate historical metric cards dynamically.
* **Rate Limiting & Threat Intelligence Webhooks:** Implement API throttling/rate limiting on the FastAPI endpoints using packages like `slowapi` to protect against denial-of-service abuse and setup outbound Discord/Slack webhooks for critical high-confidence phishing alerts.
