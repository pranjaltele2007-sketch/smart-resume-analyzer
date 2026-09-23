from flask import Flask, render_template, request
import os
from analyzer import extract_text, analyze_resume

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def home():
    results = None
    selected_role = "Web Developer"
    if request.method == 'POST':
        file = request.files.get('resume')
        selected_role = request.form.get('role', 'Web Developer')
        if file and file.filename != '':
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            try:
                text = extract_text(file_path)
                results = analyze_resume(text, selected_role)
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
    return render_template('index.html', results=results, selected_role=selected_role)

if __name__ == '__main__':
    app.run(debug=True, port=5050)