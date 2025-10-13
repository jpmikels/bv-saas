# Valuation Tool Ryan

A lightweight web application that processes PDF, Excel, and CSV files containing financial data and provides a data preview for business valuation use cases.

### Features
- Upload and extract tabular data from PDFs using **odfplumber**.
- Parse `.xlsx` and `.csv` financial statements.
- Simple Flask interface with a single-page upload form.
- Cloud-ready: deploy easily to **Google Cloud Run** or **Docker**.

### Folder Structure
```
valuation-tool-ryan/
├── app.py
├── templates/
│   └── index.html
├── requirements.txt
├── Dockerfile
├── README.md
└── uploads/
```

### Run Locally
```bash
pip install -r requirements.txt
python app.py
```

### Deploy to Cloud Run
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/valuation-app
gcloud run deploy valuation-app \
  --image gcr.io/PROJECT_ID/valuation-app \
  --allow-unauthenticated \
  --port 8080
```
