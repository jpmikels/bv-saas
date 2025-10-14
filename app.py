from flask import Flask, request, render_template, jsonify
import pandas as pd
import pdfplumber
import os

MONTH_TOKENS = {"jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec","total"}

def parse_excel_smart(path: str, sheet_name=0, preview_rows=5):
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None)

    def looks_like_header(row: pd.Series) -> bool:
        vals = [str(x).strip().lower() for x in row.dropna().tolist()]
        return any(any(tok in v for tok in MONTH_TOKENS) for v in vals)

    header_row_idx = None
    for i in range(min(15, len(raw))):
        if looks_like_header(raw.iloc[i]):
            header_row_idx = i
            break

    if header_row_idx is None:
        header_row_idx = raw.iloc[:15].notna().sum(axis=1).idxmax()

    df = pd.read_excel(path, sheet_name=sheet_name, header=None, skiprows=header_row_idx)
    df.columns = df.iloc[0].astype(str).str.strip()
    df = df.iloc[1:]
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    first_col = df.columns[0]
    df[first_col] = df[first_col].ffill()
    return df.reset_index(drop=True).to_dict(orient="records")[:preview_rows]

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB

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
   elif fname.endswith(('.xlsx', '.xls')):
    data = parse_excel_smart(filepath, preview_rows=5)
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
