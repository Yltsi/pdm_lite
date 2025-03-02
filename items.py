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
        form_description = request.form.get('description', '')
        form_revision = request.args.get('revision', '')
        form_material = request.form.get('material', '')
        form_vendor = request.form.get('vendor', '')
        form_vendor_part_number = request.form.get('vendor_part_number', '')
        component_search = request.form.get('component_search', '')
        component_type_filter = request.form.get('component_type_filter', 'All')

        # Initialize for assembly BOM functionality
        available_components = []
        bom_items = []

        # Initialize these variables
        items = []
        assemblies = []
        manufactured_parts = []
        fixed_parts = []
        search_performed = False

        # Store BOM items temporarily in session
        if 'temp_bom_items' not in session:
            session['temp_bom_items'] = []

        if request.method == "POST":
            # Search components for BOM
            if 'search_components' in request.form and item_type_selected == 'Assembly':
                search_term = request.form.get('component_search', '')
                type_filter = request.form.get('component_type_filter', 'All')
                available_components = db.get_available_components(search_term, None, type_filter)
                bom_items = session.get('temp_bom_items', [])
                active_tab = 'add'
                form_description = request.form.get('description', '')

            # Add component to BOM
            elif 'add_component' in request.form and item_type_selected == 'Assembly':
                component_id = int(request.form.get('component_id', 0))
                component_qty = int(request.form.get('component_qty', 1))
                description = request.form.get('description', '')

                if component_id > 0:
                    # Check if component already exists in the BOM
                    existing_items = session.get('temp_bom_items', [])
                    component_exists = False

                    for item in existing_items:
                        if item['item_number'] == component_id:
                            component_exists = True
                            flash(f"Component {component_id} already exists in the BOM", "error")
                            break

                    # Check for circular reference
                    if db.check_circular_reference(None, component_id):
                        component_exists = True
                        flash(f"Cannot add component {component_id} - would create circular reference", "error")

                    # If component doesn't exist in BOM, add it with next line number
                    if not component_exists:
                        component = db.get_item_by_number(component_id)
                        if component:
                            line_number = 10 if not existing_items else max([item['line_number'] for item in existing_items]) + 10
                            new_item = {
                                'line_number': line_number,
                                'item_number': component_id,
                                'description': component['description'],
                                'quantity': component_qty
                            }
                            existing_items.append(new_item)
                            session['temp_bom_items'] = existing_items
                            flash(f"Component {component_id} added to BOM", "success")

                # Refresh component list and BOM items
                search_term = request.form.get('component_search', '')
                if search_term:
                    available_components = db.get_available_components(search_term)
                bom_items = session.get('temp_bom_items', [])
                form_description = description
                active_tab = 'add'

            # Remove component from BOM
            elif 'remove_component' in request.form and item_type_selected == 'Assembly':
                line_number = int(request.form.get('line_number', 0))
                description = request.form.get('description', '')

                if line_number > 0:
                    existing_items = session.get('temp_bom_items', [])
                    updated_items = [item for item in existing_items if item['line_number'] != line_number]
                    session['temp_bom_items'] = updated_items
                    flash(f"Component with line {line_number} removed from BOM", "success")

                # Refresh component list and BOM items
                search_term = request.form.get('component_search', '')
                if search_term:
                    available_components = db.get_available_components(search_term)
                bom_items = session.get('temp_bom_items', [])
                form_description = description
                active_tab = 'add'

            # Update component quantity
            elif 'update_qty' in request.form and item_type_selected == 'Assembly':
                line_number = int(request.form.get('line_number', 0))
                component_qty = int(request.form.get('component_qty', 1))
                description = request.form.get('description', '')

                if line_number > 0:
                    existing_items = session.get('temp_bom_items', [])
                    for item in existing_items:
                        if item['line_number'] == line_number:
                            item['quantity'] = component_qty
                            flash(f"Updated quantity for component at line {line_number}", "success")
                            break

                    session['temp_bom_items'] = existing_items

                # Refresh component list and BOM items
                search_term = request.form.get('component_search', '')
                if search_term:
                    available_components = db.get_available_components(search_term)
                bom_items = session.get('temp_bom_items', [])
                form_description = description
                active_tab = 'add'

            elif 'searchform' in request.form:
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
                revision = request.form.get("revision", "1")

                if item_type == 'Manufactured Part':
                    material = request.form.get("material")
                    success = db.add_manufactured_part(description, revision, username, material)
                elif item_type == 'Fixed Part':
                    vendor = request.form.get("vendor")
                    vendor_part_number = request.form.get("vendor_part_number")
                    success = db.add_fixed_part(description, revision, username,
                                                vendor, vendor_part_number)
                elif item_type == 'Assembly':
                    # Get BOM items from session
                    bom_items = session.get('temp_bom_items', [])

                    # Create a formatted list of BOM items for the database
                    formatted_bom = []
                    for item in bom_items:
                        formatted_bom.append({
                            'component_item_number': item['item_number'],
                            'quantity': item['quantity'],
                            'line_number': item['line_number']
                        })

                    # Add the assembly with BOM items
                    item_number = db.add_assembly(description, revision, username, formatted_bom)

                    if item_number:
                        # Clear temporary BOM items from session
                        session['temp_bom_items'] = []
                        flash(f"Assembly '{description}' added successfully with {len(formatted_bom)} components!", "success")
                        success = True
                    else:
                        flash(f"Error adding Assembly '{description}'. Please check logs for details.", "error")
                        success = False
                else:
                    success = False

                if success:
                    flash(f"{item_type} '{description}' added successfully!", "success")
                else:
                    flash(f"Error adding {item_type} '{description}'. Please check inputs and try again.", "error")
                active_tab = 'add'

            # If item type changed, clear temp BOM items
            if 'item_type' in request.form and request.form.get('item_type') != 'Assembly':
                session['temp_bom_items'] = []

        else:
            items_rows = db.get_all_items()
            for row in items_rows:
                item_dict = dict(row)
                items.append(item_dict)
            assemblies = db.get_assemblies()
            manufactured_parts = db.get_manufactured_parts()
            fixed_parts = db.get_fixed_parts()

        # Always retrieve BOM items from session if in Assembly mode
        if item_type_selected == 'Assembly':
            bom_items = session.get('temp_bom_items', [])

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
            form_vendor_part_number=form_vendor_part_number,
            component_search=component_search,
            component_type_filter=component_type_filter,
            available_components=available_components,
            bom_items=bom_items
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
        available_components = []

        # Initialize or retrieve temp BOM from session
        if 'temp_edit_bom' not in session or session.get('temp_edit_item_number') != item_number:
            session['temp_edit_item_number'] = item_number
            session['temp_edit_bom'] = []

            # Load current BOM into session if this is an Assembly
            if item["item_type"] == "Assembly":
                try:
                    # Use the normal get_assembly_bom function but with better error handling
                    bom_items = db.get_assembly_bom(item_number)
                    if bom_items:
                        # Convert SQLite rows to dicts for session storage
                        for bom_item in bom_items:
                            # Access attributes directly with square brackets instead of using .get()
                            session['temp_edit_bom'].append({
                                'line_number': bom_item['line_number'],
                                'component_item_number': bom_item['component_item_number'],
                                'quantity': bom_item['quantity'],
                                'description': bom_item['description'],
                                'item_type': bom_item['item_type'] if 'item_type' in bom_item else 'Unknown'
                            })
                except Exception as e:
                    flash(f"Error loading assembly BOM: {str(e)}", "error")
                    print(f"BOM loading error details: {e}")

        bom_items = session.get('temp_edit_bom', [])

        if item["item_type"] == "Manufactured Part":
            manufactured_part = db.get_manufactured_part_details(item_number)
        elif item["item_type"] == "Fixed Part":
            fixed_part = db.get_fixed_part_details(item_number)

        # Handle component search if this is a POST request
        if request.method == "POST" and "search_components" in request.form:
            search_term = request.form.get("component_search", "")
            type_filter = request.form.get("component_type_filter", "All")
            available_components = db.get_available_components(search_term, item_number, type_filter)

        return render_template("edit_item.html",
                              item=item,
                              manufactured_part=manufactured_part,
                              fixed_part=fixed_part,
                              bom_items=bom_items,
                              available_components=available_components)
    return redirect("/")

def update_item(item_number):
    """Updates an item in the database."""
    if "username" in session:
        username = session["username"]

        # Get the current item
        item = db.get_item_by_number(item_number)
        if not item:
            flash("Item not found", "error")
            return redirect("/pdm")

        item_type = item["item_type"]
        current_revision = item["revision"]
        description = request.form.get("description", item["description"])

        # Handle standard item update or assembly update with "Update Item" button
        if "update_item" in request.form:
            try:
                new_revision = int(current_revision) + 1
            except ValueError:
                new_revision = 1

            # Standard update for all item types
            if db.update_item_base(item_number, item_type, description, str(new_revision), username):
                # Additional type-specific updates
                if item_type == "Manufactured Part":
                    material = request.form.get("material", "")
                    db.update_manufactured_parts_details(item_number, description, material, str(new_revision))
                elif item_type == "Fixed Part":
                    vendor = request.form.get("vendor", "")
                    vendor_part_number = request.form.get("vendor_part_number", "")
                    db.update_fixed_parts_details(item_number, description, vendor, vendor_part_number, str(new_revision))
                elif item_type == "Assembly":
                    # Get BOM data from the form
                    line_numbers = request.form.getlist('bom_line_numbers[]')
                    component_ids = request.form.getlist('bom_component_ids[]')
                    quantities = request.form.getlist('bom_quantities[]')
                    remove_lines = request.form.getlist('remove_component_lines[]')

                    # Get existing BOM items from session
                    existing_bom = session.get('temp_edit_bom', [])

                    # Create updated BOM list (excluding removed lines)
                    updated_bom = []
                    for i in range(len(line_numbers)):
                        line_number = line_numbers[i]

                        # Skip if this line was marked for removal
                        if line_number in remove_lines:
                            continue

                        # Find component details from the session data
                        for item in existing_bom:
                            if str(item['line_number']) == line_number:
                                updated_bom.append({
                                    'line_number': int(line_number),
                                    'component_item_number': int(component_ids[i]),
                                    'quantity': int(quantities[i]),
                                    'description': item.get('description', ''),
                                    'item_type': item.get('item_type', 'Unknown')
                                })
                                break

                    try:
                        # Use transaction-safe BOM update
                        success = db.update_assembly_bom(item_number, updated_bom, str(new_revision))

                        if success:
                            # Clear session BOM data
                            session.pop('temp_edit_bom', None)
                            session.pop('temp_edit_item_number', None)

                            flash(f"Assembly BOM updated successfully with {len(updated_bom)} components", "success")
                        else:
                            flash("Error updating assembly BOM. Please try again.", "error")
                            return redirect(f"/edit_item/{item_number}")
                    except Exception as e:
                        flash(f"Error updating assembly BOM: {str(e)}", "error")
                        return redirect(f"/edit_item/{item_number}")

                flash(f"{item_type} \"{description}\" (Item Number: {item_number}) updated to revision {new_revision}!", "success")
                return redirect("/pdm")
            else:
                flash("Error updating item base information. Please check logs.", "error")
                return redirect(f"/edit_item/{item_number}")

        # Handle BOM session manipulation for Assembly items
        elif item_type == "Assembly":
            temp_bom = session.get('temp_edit_bom', [])
            template_context = {
                "item": item,
                "manufactured_part": None,
                "fixed_part": None,
                "bom_items": temp_bom,
                "available_components": []
            }

            # Add component to temp BOM
            if "add_component" in request.form:
                component_id = request.form.get("add_component_id")

                if component_id:
                    component_id = int(component_id)
                    component_qty = int(request.form.get(f"add_qty_{component_id}", 1))

                    # Check for circular reference
                    if db.check_circular_reference(item_number, component_id):
                        flash(f"Cannot add component {component_id} - would create circular reference", "error")
                    else:
                        # Check if component already exists
                        exists = False
                        for bom_item in temp_bom:
                            if bom_item['component_item_number'] == component_id:
                                exists = True
                                flash(f"Component {component_id} already exists in the BOM", "error")
                                break

                        if not exists:
                            # Get component details
                            component = db.get_item_by_number(component_id)
                            if component:
                                # Calculate next line number
                                line_number = 10
                                if temp_bom:
                                    line_number = max([item['line_number'] for item in temp_bom]) + 10

                                # Add to temp BOM
                                temp_bom.append({
                                    'line_number': line_number,
                                    'component_item_number': component_id,
                                    'quantity': component_qty,
                                    'description': component['description'],
                                    'item_type': component['item_type']
                                })
                                session['temp_edit_bom'] = temp_bom
                                flash(f"Component {component_id} added to BOM (will be saved when you click 'Update Item')", "success")

                # Keep search results
                search_term = request.form.get("component_search", "")
                type_filter = request.form.get("component_type_filter", "All")
                template_context["available_components"] = db.get_available_components(search_term, item_number, type_filter)
                template_context["bom_items"] = temp_bom

                return render_template("edit_item.html", **template_context)

            # Component search
            elif "search_components" in request.form:
                search_term = request.form.get("component_search", "")
                type_filter = request.form.get("component_type_filter", "All")
                template_context["available_components"] = db.get_available_components(search_term, item_number, type_filter)
                template_context["bom_items"] = temp_bom

                return render_template("edit_item.html", **template_context)

        # If we got here without returning, something unexpected happened
        flash("Invalid operation. Please try again.", "error")
        return redirect(f"/edit_item/{item_number}")
    return redirect("/")

def delete_item(item_number):
    """Deletes an item from the database."""
    if "username" not in session:
        return redirect("/")

    try:
        item = db.get_item_by_number(item_number)
        if not item:
            flash(f"Item Number {item_number} not found", "error")
            return redirect("/pdm")

        # Check if the item is used in any assemblies
        con = db.get_connection()
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM assemblies WHERE component_item_number = ?", (item_number,))
        result = cursor.fetchone()
        con.close()

        if result and result['count'] > 0:
            flash(f"Cannot delete Item Number {item_number} because it is used in {result['count']} assemblies. Remove it from all assemblies first.", "error")
            return redirect("/pdm")

        # Attempt to delete the item
        if db.delete_item_by_number(item_number):
            flash(f"Item Number {item_number} deleted successfully!", "success")
        else:
            flash(f"Error deleting Item Number {item_number}. It may be referenced by other items or the database is busy.", "error")
    except Exception as e:
        flash(f"Error during item deletion: {str(e)}", "error")

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

def item_details(item_number):
    """Display detailed information about an item and its revision history."""
    if "username" not in session:
        return redirect("/")

    item = db.get_item_by_number(item_number)
    if not item:
        flash("Item not found", "error")
        return redirect("/pdm")

    revisions = db.get_item_revisions(item_number)

    # Get specific details based on item type
    specific_details = None
    bom_items = []

    if item["item_type"] == "Manufactured Part":
        specific_details = db.get_manufactured_part_details(item_number)
    elif item["item_type"] == "Fixed Part":
        specific_details = db.get_fixed_part_details(item_number)
    elif item["item_type"] == "Assembly":
        # Get BOM items for this assembly
        bom_items = db.get_assembly_bom(item_number)

    return render_template(
        "item_details.html", 
        item=item,
        specific_details=specific_details,
        bom_items=bom_items,
        revisions=revisions,
        username=session["username"]
    )
