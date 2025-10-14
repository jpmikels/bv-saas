from flask import Flask, request, render_template, jsonify, send_file
import pandas as pd
import pdfplumber
import os
import io
import re

app = Flask(__name__)

# ---- Limits & upload folder ----
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB request limit (Cloud Run)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---- Smart Excel header detection ----
MONTH_TOKENS = {"jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec","total"}

def parse_excel_smart(path: str, sheet_name=0):
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
    return df.reset_index(drop=True)

# ---- PDF tables → DataFrame ----
def parse_pdf_tables(path: str) -> pd.DataFrame:
    frames = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                frames.append(df)
    if frames:
        df = pd.concat(frames, ignore_index=True)
        df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
        return df
    return pd.DataFrame()

# ---- Very simple sheet classifier ----
_PNL_KW = re.compile(r"(p&l|profit|income\s*statement|revenue)", re.I)
_BS_KW  = re.compile(r"(balance\s*sheet|assets|liabilities|equity)", re.I)
_CF_KW  = re.compile(r"(cash\s*flow|operating\s*activities|investing\s*activities|financing\s*activities)", re.I)

def classify_sheet(df: pd.DataFrame, fname: str) -> str:
    name = fname.lower()
    head_vals = " ".join(map(str, df.head(5).values.flatten())).lower()
    if _PNL_KW.search(name) or _PNL_KW.search(head_vals): return "P&L"
    if _BS_KW.search(name)  or _BS_KW.search(head_vals):  return "Balance Sheet"
    if _CF_KW.search(name)  or _CF_KW.search(head_vals):  return "Cash Flow"
    return "Other"

# ---- Routes ----
@app.route('/')
def index():
    return render_template('index.html')

# Multi-file upload → consolidated Excel response
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        files = request.files.getlist('files')  # <-- expects <input name="files" multiple>
        if not files:
            return jsonify(error='No files uploaded'), 400

        buckets = {"P&L": [], "Balance Sheet": [], "Cash Flow": [], "Other": []}

        for f in files:
            if not f or f.filename == '':
                continue
            fname = f.filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
            f.save(save_path)

            lname = fname.lower()
            if lname.endswith(('.xlsx', '.xls')):
                df = parse_excel_smart(save_path)
            elif lname.endswith('.csv'):
                df = pd.read_csv(save_path)
            elif lname.endswith('.pdf'):
                df = parse_pdf_tables(save_path)
            else:
                df = pd.DataFrame()

            if df is None or df.empty:
                continue

            # trace back source
            df.insert(0, 'Source File', fname)
            buckets[classify_sheet(df, fname)].append(df)

        merged = {k: (pd.concat(v, ignore_index=True) if v else pd.DataFrame())
                  for k, v in buckets.items()}

        # build Excel in-memory and return
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            for sheet, frame in merged.items():
                if not frame.empty:
                    frame.to_excel(writer, sheet_name=sheet[:31], index=False)
        buf.seek(0)
        return send_file(
            buf,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="valuation_consolidated.xlsx"
        )
    except Exception as e:
        app.logger.exception("Upload failed")
        return jsonify(error=str(e)), 500

# ---- Cloud Run entrypoint ----
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
