from flask import Flask, request, render_template, jsonify
import pandas as pd
import pdfplumber
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file:
        return 'No file uploaded', 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    if file.filename.endswith('.pdf'):
        data = extract_pdf_data(filepath)
    elif file.filename.endswith('.xlsx'):
        data = pd.read_excel(filepath).to_dict(orient='records')
    elif file.filename.endswith('.csv'):
        data = pd.read_csv(filepath).to_dict(orient='records')
    else:
        return 'Unsupported file type', 400

    return jsonify({'data_preview': data[:5]})

def extract_pdf_data(path):
    extracted_data = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                extracted_data.extend(df.to_dict(orient='records'))
    return extracted_data

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
