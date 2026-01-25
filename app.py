from flask import Flask, render_template, request
import os

app = Flask(__name__)

def update_logic(form_data):
    # Files to maintain
    files = [
        "DAILY_DIARY_Chandan_Panwar_2025_08.csv",
        "DAILY_DIARY_Chandan_Panwar_2025_09.csv"
    ]
    
    date_val = form_data['date']
    month_of_entry = date_val.split("-")[1] # '08' or '09'

    for filename in files:
        if not os.path.exists(filename): continue

        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            # A. Update Headers (Name, Post, Office, RO)
            if "क्षेत्र कर्मचारी/अधिकारी का नाम:" in line:
                line = f"क्षेत्र कर्मचारी/अधिकारी का नाम: {form_data['name']},,,,,पदनाम: {form_data['post']},,,,उ॰क्षे॰का॰/स्था॰उप॰क्षे॰का॰: {form_data['office']},,,,क्षेत्रीय कार्यालय: {form_data['ro']} ,,\n"
            
            # B. Update Table Row (Only if date matches the row in current file)
            if line.startswith(date_val):
                cols = line.split(',')
                while len(cols) < 15: cols.append('')
                cols[4] = form_data['mode']
                cols[5] = form_data['dist']
                cols[6] = form_data['fare']
                cols[10] = form_data['work']
                cols[12] = form_data['time']
                line = ','.join(cols) + "\n"

            new_lines.append(line)

        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return "Header and Data updated in both files successfully!"

@app.route('/')
def home(): return render_template('index.html')

@app.route('/sync_update', methods=['POST'])
def sync():
    msg = update_logic(request.form)
    return f"<h3>{msg}</h3><a href='/'>Go Back</a>"

if __name__ == '__main__':
    app.run(debug=True)
