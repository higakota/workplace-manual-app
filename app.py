import json
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATA_FILE = 'menus.json'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_menus():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    return {}

def save_menus(menus):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(menus, f, ensure_ascii=False, indent=4)

@app.route("/")
def index():
    menus = load_menus()
    return render_template("index.html", menus=menus)

@app.route("/menu/<int:menu_id>")
def detail(menu_id):
    menus = load_menus()
    menu = menus.get(menu_id)
    return render_template("detail.html", menu=menu)

@app.route("/search")
def search():
    menus = load_menus()
    query = request.args.get("q", "")
    results = {id: m for id, m in menus.items() if query.lower() in m["name"].lower()}
    return render_template("index.html", menus=results, query=query)

@app.route("/admin")
def admin():
    menus = load_menus()
    return render_template("admin.html", menus=menus)

@app.route("/admin/save", methods=["POST"])
def save_item():
    menus = load_menus()
    menu_id = request.form.get("id")
    file = request.files.get('image')
    image_url = request.form.get('existing_image', '')
    
    if file and file.filename != '':
        
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        
        
        new_filename = str(uuid.uuid4()) + ext
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
        image_url = '/static/uploads/' + new_filename

    new_data = {
        "name": request.form.get("name"),
        "category": request.form.get("category"),
        "recipe": request.form.get("recipe"),
        "hot": request.form.get("hot"),
        "ice": request.form.get("ice"),
        "image": image_url
    }
    
    if menu_id and menu_id.isdigit():
        menus[int(menu_id)] = new_data
    else:
        new_id = max(menus.keys()) + 1 if menus else 1
        menus[new_id] = new_data
    
    save_menus(menus)
    return redirect(url_for('admin'))

@app.route("/admin/delete/<int:menu_id>")
def delete_item(menu_id):
    menus = load_menus()
    if menu_id in menus:
        del menus[menu_id]
        save_menus(menus)
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)