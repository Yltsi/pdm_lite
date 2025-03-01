"""Item management functions for PDM Lite."""
from flask import render_template, request, session, redirect, flash
import db

def pdm():
    """Product Data Management page."""
    if "username" in session:
        username = session["username"]
        active_tab = request.args.get('tab', 'search')
        item_type_selected = (request.args.get('item_type') or
                              request.form.get('item_type', 'Manufactured Part'))
        form_description = request.args.get('description', '')
        form_revision = request.args.get('revision', '')
        form_material = request.args.get('material', '')
        form_vendor = request.args.get('vendor', '')
        form_vendor_part_number = request.args.get('vendor_part_number', '')

        search_performed = False
        items = []
        assemblies = []
        manufactured_parts = []
        fixed_parts = []

        if request.method == "POST":
            if 'searchform' in request.form:
                search_description = request.form.get("search_description")
                item_filter = request.form.get("item_filter")
                items_rows = db.search_items_db(search_description, item_filter)
                for row in items_rows:
                    item_dict = dict(row)
                    items.append(item_dict)
                active_tab = 'search'
                search_performed = True

            elif 'additemform' in request.form:
                item_type = request.form.get("item_type")
                description = request.form.get("description")
                revision = request.form.get("revision")

                if item_type == 'Manufactured Part':
                    material = request.form.get("material")
                    success = db.add_manufactured_part(description, revision, username, material)
                elif item_type == 'Fixed Part':
                    vendor = request.form.get("vendor")
                    vendor_part_number = request.form.get("vendor_part_number")
                    success = db.add_fixed_part(description, revision, username,
                                                vendor, vendor_part_number)
                elif item_type == 'Assembly':
                    success = db.add_assembly(description, revision, username)
                else:
                    success = False

                if success:
                    flash(f"{item_type} '{description}' lisätty onnistuneesti!", "success")
                else:
                    flash(f"Virhe lisättäessä {item_type} '{description}'. Tarkista tiedot ja yritä uudelleen.", "error")
                active_tab = 'add'

        else:
            items_rows = db.get_all_items()
            for row in items_rows:
                item_dict = dict(row)
                items.append(item_dict)
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
            active_tab=active_tab,
            item_type_selected=item_type_selected,
            search_performed=search_performed,
            flashes=session.get('_flashes', []),
            form_description=form_description,
            form_revision=form_revision,
            form_material=form_material,
            form_vendor=form_vendor,
            form_vendor_part_number=form_vendor_part_number
        )
    return redirect("/")

def add_item():
    """Adds a new item to the database."""
    if "username" not in session:
        return redirect("/")

    if request.method == "POST":
        username = session["username"]
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

def search_items():
    """Searches the items database for items matching the search criteria."""
    if "username" in session:
        search_description = request.form.get("search_description", "")
        item_filter = request.form.get("item_filter", "All")
        search_results = db.search_items_db(search_description, item_filter)
        return render_template("pdm.html", search_results=search_results, search_performed=True)
    return redirect("/")

def edit_item(item_number):
    """Displays the edit item page."""
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
    return redirect("/")

def update_item(item_number):
    """Updates an item in the database."""
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
                db.update_manufactured_parts_details(item_number, description,
                                                     material, str(new_revision))
            elif item_type == "Fixed Part":
                vendor = request.form["vendor"]
                vendor_part_number = request.form["vendor_part_number"]
                db.update_fixed_parts_details(item_number, description, vendor,
                                              vendor_part_number, str(new_revision))
            flash(f"{item_type} \"{description}\" (Item Number: {item_number}) updated to revision {new_revision}!", "success")
            return redirect("/pdm")
        flash("Error updating item. Please check logs.", "error")
        return redirect(f"/edit_item/{item_number}")
    return redirect("/")

def delete_item(item_number):
    """Deletes an item from the database."""
    if "username" in session:
        if db.delete_item_by_number(item_number):
            flash(f"Item Number {item_number} deleted successfully!", "success")
        else:
            flash(f"Error deleting Item Number {item_number}. Please check logs.", "error")
    else:
        return redirect("/")
    return redirect("/pdm")

def user_page():
    """Displays the user page."""
    if "username" in session:
        username = session["username"]
        user_items_rows = db.get_items_by_user(username)
        user_items = []
        for row in user_items_rows:
            user_items.append(dict(row))

        total_items_related_to_user = len(user_items)
        item_type_counts = {}
        for item in user_items:
            item_type = item['item_type']
            item_type_counts[item_type] = item_type_counts.get(item_type, 0) + 1

        return render_template(
            "user_page.html",
            username=username,
            user_items=user_items,
            total_items_created=total_items_related_to_user,
            item_type_counts=item_type_counts
        )
    return redirect("/")
