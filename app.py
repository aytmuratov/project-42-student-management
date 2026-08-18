from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
DB = 'students.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            grade TEXT NOT NULL,
            age INTEGER NOT NULL
        )''')

BASE = '''
<!DOCTYPE html>
<html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Student Management</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#f0f2f5;color:#333}
.nav{background:linear-gradient(135deg,#11998e,#38ef7d);padding:1rem 2rem;display:flex;justify-content:space-between;align-items:center}
.nav a{color:#fff;text-decoration:none;margin:0 1rem;font-weight:500}
.nav h1{color:#fff;font-size:1.4rem}
.container{max-width:1100px;margin:2rem auto;padding:0 1rem}
.card{background:#fff;border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.card h2{color:#11998e;margin-bottom:1rem}
.form-group{margin-bottom:1rem}
.form-group label{display:block;font-weight:600;margin-bottom:.3rem}
.form-group input,.form-group select{width:100%;padding:.6rem;border:1px solid #ddd;border-radius:8px;font-size:.95rem}
.btn{padding:.6rem 1.5rem;border:none;border-radius:8px;cursor:pointer;font-size:.95rem;font-weight:600;color:#fff}
.btn-primary{background:linear-gradient(135deg,#11998e,#38ef7d)}
.btn-danger{background:#e74c3c}
.btn-edit{background:#3498db}
.btn:hover{opacity:.85}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:1.5rem}
.stat-card{background:#fff;border-radius:12px;padding:1.5rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.stat-card h3{font-size:2rem;color:#11998e}
.stat-card p{color:#888;margin-top:.3rem}
table{width:100%;border-collapse:collapse}
th,td{padding:.7rem;text-align:left;border-bottom:1px solid #eee}
th{background:#f8f9fa;color:#555}
.actions a{margin-right:.5rem}
</style>
</head><body>
<div class="nav">
<h1>Student Management</h1>
<div>
<a href="/">Dashboard</a>
<a href="/add">Add Student</a>
</div>
</div>
<div class="container">
'''

@app.route('/')
def index():
    db = get_db()
    students = db.execute('SELECT * FROM students ORDER BY name').fetchall()
    total = len(students)
    avg = db.execute('SELECT COALESCE(AVG(age),0) as a FROM students').fetchone()['a']
    grades = db.execute('SELECT grade, COUNT(*) as c FROM students GROUP BY grade').fetchall()
    return render_template_string(BASE + '''
<div class="stats">
<div class="stat-card"><h3>{{ total }}</h3><p>Total Students</p></div>
<div class="stat-card"><h3>{{ "%.1f"|format(avg) }}</h3><p>Average Age</p></div>
<div class="stat-card"><h3>{{ grades|length }}</h3><p>Grade Groups</p></div>
</div>
<div class="card"><h2>All Students</h2>
<form method="GET" action="/search" style="margin-bottom:1rem;display:flex;gap:.5rem">
<input type="text" name="q" placeholder="Search students..." style="flex:1;padding:.6rem;border:1px solid #ddd;border-radius:8px">
<button type="submit" class="btn btn-primary">Search</button>
</form>
<table><tr><th>Name</th><th>Email</th><th>Grade</th><th>Age</th><th>Actions</th></tr>
{% for s in students %}
<tr><td>{{ s.name }}</td><td>{{ s.email }}</td><td>{{ s.grade }}</td><td>{{ s.age }}</td>
<td class="actions">
<a href="/edit/{{ s.id }}" class="btn btn-edit">Edit</a>
<a href="/delete/{{ s.id }}" class="btn btn-danger" onclick="return confirm('Delete?')">Delete</a>
</td></tr>
{% endfor %}
</table></div>
</div></body></html>
''', students=students, total=total, avg=avg, grades=grades)

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        db = get_db()
        db.execute('INSERT INTO students (name,email,grade,age) VALUES (?,?,?,?)',
                   (request.form['name'], request.form['email'], request.form['grade'], int(request.form['age'])))
        db.commit()
        return redirect(url_for('index'))
    return render_template_string(BASE + '''
<div class="card"><h2>Add Student</h2>
<form method="POST">
<div class="form-group"><label>Name</label><input type="text" name="name" required></div>
<div class="form-group"><label>Email</label><input type="email" name="email" required></div>
<div class="form-group"><label>Grade</label>
<select name="grade"><option>A</option><option>B</option><option>C</option><option>D</option><option>F</option></select></div>
<div class="form-group"><label>Age</label><input type="number" name="age" required></div>
<button type="submit" class="btn btn-primary">Add Student</button>
</form></div>
</div></body></html>
''')

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    db = get_db()
    if request.method == 'POST':
        db.execute('UPDATE students SET name=?,email=?,grade=?,age=? WHERE id=?',
                   (request.form['name'], request.form['email'], request.form['grade'], int(request.form['age']), id))
        db.commit()
        return redirect(url_for('index'))
    s = db.execute('SELECT * FROM students WHERE id=?', (id,)).fetchone()
    return render_template_string(BASE + '''
<div class="card"><h2>Edit Student</h2>
<form method="POST">
<div class="form-group"><label>Name</label><input type="text" name="name" value="{{ s.name }}" required></div>
<div class="form-group"><label>Email</label><input type="email" name="email" value="{{ s.email }}" required></div>
<div class="form-group"><label>Grade</label>
<select name="grade">
{% for g in ['A','B','C','D','F'] %}
<option {{ 'selected' if g==s.grade else '' }}>{{ g }}</option>
{% endfor %}</select></div>
<div class="form-group"><label>Age</label><input type="number" name="age" value="{{ s.age }}" required></div>
<button type="submit" class="btn btn-primary">Update</button>
</form></div>
</div></body></html>
''', s=s)

@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    db.execute('DELETE FROM students WHERE id=?', (id,))
    db.commit()
    return redirect(url_for('index'))

@app.route('/search')
def search():
    q = request.args.get('q','')
    db = get_db()
    students = db.execute('SELECT * FROM students WHERE name LIKE ? OR email LIKE ? OR grade LIKE ?',
                          (f'%{q}%',f'%{q}%',f'%{q}%')).fetchall()
    return render_template_string(BASE + '''
<div class="card"><h2>Search: "{{ q }}"</h2>
<table><tr><th>Name</th><th>Email</th><th>Grade</th><th>Age</th><th>Actions</th></tr>
{% for s in students %}
<tr><td>{{ s.name }}</td><td>{{ s.email }}</td><td>{{ s.grade }}</td><td>{{ s.age }}</td>
<td class="actions">
<a href="/edit/{{ s.id }}" class="btn btn-edit">Edit</a>
<a href="/delete/{{ s.id }}" class="btn btn-danger" onclick="return confirm('Delete?')">Delete</a>
</td></tr>
{% endfor %}
</table><p style="margin-top:1rem"><a href="/">Back to Dashboard</a></p></div>
</div></body></html>
''', students=students, q=q)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
