import sqlite3
from flask import Flask, redirect, render_template, request, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/", methods = ["GET", "POST"])
def index():
    error_message = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT password_hash FROM users WHERE username = ?"
        password_hash = db.query(sql, [username])
        
        if not password_hash:
            error_message = "Invalid username or password"
        else:
            password_hash = password_hash[0][0]
            if check_password_hash(password_hash, password):
                session["username"] = username
                return redirect("/pdm")
            else:
                error_message = "Invalid username or password"

    return render_template("index.html", error_message=error_message)

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        error_message = None
        success_message = None
        if len(password1) < 4:
            error_message = "Password must be at least 4 characters long"
        elif password1 != password2:
            error_message = "Passwords do not match"
        elif len(username) < 4:
            error_message = "Username must be at least 4 characters long"
        else:
            password_hash = generate_password_hash(password1)
            try:
                sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
                db.execute(sql, [username, password_hash])
                success_message = "Account created successfully"
            except sqlite3.IntegrityError:
                error_message = "Username is already in use"
            
        return render_template("register.html", error_message=error_message, success_message=success_message)
    else:
        return render_template("register.html")
    
@app.route("/pdm", methods=["GET", "POST"])
def pdm():
    if "username" in session:
        username = session["username"]
        active_tab = request.args.get('tab', 'search')

        if request.method == "POST":
            search_description = request.form.get("search_description")
            item_filter = request.form.get("item_filter")

            items_rows = db.search_items_db(search_description, item_filter)
            items = []
            for row in items_rows:
                item_dict = dict(row)
                items.append(item_dict)
        else:
            items = db.get_items()

        assemblies = db.get_assemblies()
        manufactured_parts = db.get_manufactured_parts()
        fixed_parts = db.get_fixed_parts()


        return render_template(
            "pdm.html",
            username=username,
            items=items,
            assemblies=assemblies,
            manufactured_parts=manufactured_parts,
            fixed_parts=fixed_parts,
            active_tab=active_tab
        )
    else:
        return redirect("/")
    
@app.route("/add_item", methods=["POST"])
def add_item():
    if request.method == "POST":
        username = session["username"]
        print("Request Form Data:", request.form)
        item_type = request.form["item_type"]
        description = request.form["description"]
        revision = request.form["revision"]

        if not item_type or not description or not revision:
            flash("All fields are required", "error")
            return redirect("/pdm")
        item_number = db.add_item_base(item_type, description, revision, username)

        if item_number:
            if item_type == "Manufactured Part":
                material = request.form.get("material")
                if material:
                    if db.add_manufactured_parts_details(item_number, description, material, revision):
                        flash(f"{item_type} \"{description}\" (Item Number: {item_number}) added successfully!", "success")
                    else:
                        flash(f"Error adding details for Manufactured Part (Item Number: {item_number}).", "error")
                else:
                    flash(f"{item_type} \"{description}\" (Item Number: {item_number}) added successfully (without material).", "success")

            elif item_type == "Fixed Part":
                vendor = request.form.get("vendor")
                vendor_part_number = request.form.get("vendor_part_number")
                if vendor and vendor_part_number:
                    if db.add_fixed_part_details(item_number, description, vendor, vendor_part_number, revision):
                        flash(f"{item_type} \"{description}\" (Item Number: {item_number}) added successfully!", "success")
                    else:
                        flash(f"Error adding details for Fixed Part (Item Number: {item_number}).", "error")
                else:
                    flash(f"Vendor and Vendor Part Number are required for Fixed Parts. Base item added with Item Number: {item_number}, but details not saved.", "warning")

            elif item_type == "Assembly":
                flash(f"{item_type} \"{description}\" (Item Number: {item_number}) added successfully!", "success")
            else:
                flash("Invalid Item Type.", "error")

        else:
            flash("Error adding base item. Please check logs.", "error")

        return redirect("/pdm")
    
@app.route("/search_items", methods=["POST"])
def search_items():
    if "username" in session:
        search_description = request.form.get("search_description", "")
        item_filter = request.form.get("item_filter", "All")
        search_results = db.search_items_db(search_description, item_filter)
        return render_template("pdm.html", search_results=search_results, search_performed=True)
    else:
        return redirect("/")
    
@app.route("/edit_item/<int:item_number>")
def edit_item(item_number):
    if "username" in session:
        item = db.get_item_by_number(item_number)
        if not item:
            flash("Item not found", "error")
            return redirect("/pdm")

        manufactured_part = None
        fixed_part = None

        if item["item_type"] == "Manufactured Part":
            manufactured_part = db.get_manufactured_part_details(item_number)
        elif item["item_type"] == "Fixed Part":
            fixed_part = db.get_fixed_part_details(item_number)

        return render_template("edit_item.html", item=item, manufactured_part=manufactured_part, fixed_part=fixed_part)
    else:
        return redirect("/")

@app.route("/update_item/<int:item_number>", methods=["POST"])
def update_item(item_number):
    if "username" in session:
        username = session["username"]
        description = request.form["description"]

        item = db.get_item_by_number(item_number)
        if not item:
            flash("Item not found", "error")
            return redirect("/pdm")
        item_type = item["item_type"]

        current_revision = item["revision"]
        try:
            new_revision = int(current_revision) + 1
        except ValueError:
            new_revision = 1

        if db.update_item_base(item_number, item_type, description, str(new_revision), username):
            if item_type == "Manufactured Part":
                material = request.form["material"]
                db.update_manufactured_parts_details(item_number, description, material, str(new_revision))
            elif item_type == "Fixed Part":
                vendor = request.form["vendor"]
                vendor_part_number = request.form["vendor_part_number"]
                db.update_fixed_parts_details(item_number, description, vendor, vendor_part_number, str(new_revision))
            flash(f"{item_type} \"{description}\" (Item Number: {item_number}) updated to revision {new_revision}!", "success")
            return redirect("/pdm")
        else:
            flash("Error updating item. Please check logs.", "error")
            return redirect(f"/edit_item/{item_number}")
    else:
        return redirect("/")

@app.route("/delete_item/<int:item_number>", methods=["POST"])
def delete_item(item_number):
    if "username" in session:
        if db.delete_item_by_number(item_number):
            flash(f"Item Number {item_number} deleted successfully!", "success")
        else:
            flash(f"Error deleting Item Number {item_number}. Please check logs.", "error")
    else:
        return redirect("/")
    return redirect("/pdm")