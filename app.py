from flask import Flask, render_template
from database import engine
from sqlalchemy import text

app = Flask(__name__)

def load_desc_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("Select * from testtable"))
        rows = result.fetchall()

        descriptions = [row._asdict() for row in rows]
    return descriptions

@app.route('/')
def home():
    desc = load_desc_from_db()
    return render_template('index.html', desc=desc)
    

if __name__ == "__main__":
    app.run(debug=True)