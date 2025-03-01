"""Database functions for the inventory management system."""
import sqlite3
from flask import g

def get_connection():
    """Returns a connection to the database."""
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=None):
    """Executes a SQL statement and commits the transaction."""
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

def last_insert_id():
    """Returns the last inserted row ID."""
    return g.last_insert_id

def query(sql, params=None):
    """Executes a SQL query and returns the result."""
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result

def add_item_base(item_type, description, revision, creator):
    """Adds a new item to the database."""
    sql = "INSERT INTO items (item_type, description, revision, creator) VALUES (?, ?, ?, ?)"
    par = [item_type, description, revision, creator]
    execute(sql, par)
    item_number = last_insert_id()
    return item_number

def add_manufactured_parts_details(item_number, description, material, revision="A"):
    """Adds a new manufactured part to the database."""
    sql = (
        "INSERT INTO manufactured_parts "
        "(item_number, description, material, revision) "
        "VALUES (?, ?, ?, ?)"
    )
    par = [item_number, description, material, revision]
    execute(sql, par)
    return True

def add_fixed_part_details(item_number, description, vendor, vendor_part_number, revision="A"):
    """Adds a new fixed part to the database."""
    sql = (
        "INSERT INTO fixed_parts "
        "(item_number, description, vendor, vendor_part_number, revision) "
        "VALUES (?, ?, ?, ?, ?)"
    )
    par = [item_number, description, vendor, vendor_part_number, revision]
    execute(sql, par)
    return True

def add_manufactured_part(description, revision, creator, material):
    """Adds a new manufactured part to the database."""
    try:
        item_number = add_item_base("Manufactured Part", description, revision, creator)
        if item_number:
            return add_manufactured_parts_details(item_number, description, material, revision)
        return False
    except Exception as e:
        print(f"Error adding manufactured part to database: {e}")
        return False

def add_fixed_part(description, revision, creator, vendor, vendor_part_number):
    """Adds a new fixed part to the database."""
    try:
        item_number = add_item_base("Fixed Part", description, revision, creator)
        if item_number:
            return add_fixed_part_details(
                item_number,
                description,
                vendor,
                vendor_part_number,
                revision
            )
        return False
    except Exception as e:
        print(f"Error adding fixed part to database: {e}")
        return False

def add_assembly(description, revision, creator, bom_items=None):
    """Adds a new assembly to the database with BOM items."""
    try:
        item_number = add_item_base('Assembly', description, revision, creator)
        if not item_number:
            return False

        if bom_items and isinstance(bom_items, list):
            for bom_item in bom_items:
                component_item_number = bom_item.get('component_item_number')
                quantity = bom_item.get('quantity', 1)
                line_number = bom_item.get('line_number')

                # Skip if no component item number
                if not component_item_number:
                    continue

                # Add BOM item to assembly
                add_assembly_component(item_number, component_item_number, quantity, line_number, revision)

        return item_number
    except Exception as e:
        print(f"Error adding assembly: {e}")
        return False

def add_assembly_component(assembly_item_number, component_item_number, quantity, line_number, revision="1"):
    """Adds a component to an assembly's BOM."""
    try:
        sql = """
            INSERT INTO assemblies 
            (assembly_item_number, component_item_number, quantity, line_number, revision) 
            VALUES (?, ?, ?, ?, ?)
        """
        par = [assembly_item_number, component_item_number, quantity, line_number, revision]
        execute(sql, par)
        return True
    except Exception as e:
        print(f"Error adding assembly component: {e}")
        return False

def get_available_components(search_term=None, exclude_item_number=None, type_filter='All'):
    """Returns available components for assembly BOM."""
    sql = """
        SELECT item_number, item_type, description, revision
        FROM items
        WHERE 1=1
    """
    params = []

    if exclude_item_number:
        sql += " AND item_number != ?"
        params.append(exclude_item_number)

    if type_filter and type_filter != 'All':
        sql += " AND item_type = ?"
        params.append(type_filter)

    if search_term:
        sql += " AND (description LIKE ? OR item_number LIKE ?)"
        params.append(f"%{search_term}%")
        params.append(f"%{search_term}%")

    sql += " ORDER BY item_number"
    
    return query(sql, params)

def check_circular_reference(assembly_item_number, component_item_number):
    """Checks if adding a component would create a circular reference."""
    # Base case: direct circular reference
    if assembly_item_number == component_item_number:
        return True

    # Check if component is an assembly
    component = get_item_by_number(component_item_number)
    if not component or component['item_type'] != 'Assembly':
        # Not an assembly, so can't create a circular reference
        return False

    # Get all components in the component assembly
    sql = "SELECT component_item_number FROM assemblies WHERE assembly_item_number = ?"
    params = [component_item_number]
    results = query(sql, params)

    # Check each sub-component recursively
    for row in results:
        sub_component_id = row['component_item_number']
        if sub_component_id == assembly_item_number:
            return True  # Found circular reference

        if check_circular_reference(assembly_item_number, sub_component_id):
            return True  # Found circular reference deeper in the hierarchy

    return False  # No circular reference found

def get_assembly_bom(assembly_item_number):
    """Gets the BOM for an assembly."""
    sql = """
        SELECT a.line_number, a.component_item_number, a.quantity, i.description, i.item_type
        FROM assemblies a
        JOIN items i ON a.component_item_number = i.item_number
        WHERE a.assembly_item_number = ?
        ORDER BY a.line_number
    """
    params = [assembly_item_number]
    return query(sql, params)

def get_next_bom_line_number(assembly_item_number):
    """Gets the next available BOM line number for an assembly."""
    sql = """
        SELECT MAX(line_number) as max_line
        FROM assemblies
        WHERE assembly_item_number = ?
    """
    params = [assembly_item_number]
    result = query(sql, params)

    if result and result[0]['max_line'] is not None:
        # Increment by 10
        return result[0]['max_line'] + 10
        # First line starts at 10
    return 10

def get_item_by_number(item_number):
    """Returns an item by its item number."""
    sql = "SELECT * FROM items WHERE item_number = ?"
    par = [item_number]
    result = query(sql, par)
    if result:
        return result[0]
    return None

def search_items_db(search_description, item_filter):
    """Searches the items database for items matching the search criteria."""
    sql = ("SELECT item_number, item_type, description, revision, creator, revisioner "
           "FROM items "
           "WHERE 1=1")
    par = []

    if item_filter != "All":
        sql += " AND item_type = ?"
        par.append(item_filter)

    if search_description:
        sql += " AND description LIKE ?"
        par.append(f"%{search_description}%")

    sql += " ORDER BY item_number"

    results = query(sql, par)
    return results

def get_all_items():
    """Returns all items in the database."""
    sql = ("SELECT item_number, item_type, description, revision, creator, revisioner "
           "FROM items "
           "ORDER BY item_number")
    items = query(sql)
    print("get_all_items_ordered_by_number items:", items)
    return items

def get_manufactured_part_details(item_number):
    """Returns the details of a manufactured part."""
    sql = "SELECT * FROM manufactured_parts WHERE item_number = ?"
    par = [item_number]
    result = query(sql, par)
    if result:
        return result[0]
    return None

def get_fixed_part_details(item_number):
    """Returns the details of a fixed part."""
    sql = "SELECT * FROM fixed_parts WHERE item_number = ?"
    par = [item_number]
    result = query(sql, par)
    if result:
        return result[0]
    return None

def update_item_base(item_number, item_type, description, revision, username):
    """Updates item base details and saves old revision to item_revisions."""
    try:
        con = get_connection()
        cursor = con.cursor()

        current_item = get_item_by_number(item_number)
        if not current_item:
            return False

        manufactured_part_details = None
        fixed_part_details = None
        if item_type == "Manufactured Part":
            manufactured_part_details = get_manufactured_part_details(item_number)
        elif item_type == "Fixed Part":
            fixed_part_details = get_fixed_part_details(item_number)

        sql_insert_revision = """
            INSERT INTO item_revisions (item_number, revision_number, revisioner, item_type, description, material, vendor, vendor_part_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql_insert_revision, (
            item_number,
            current_item['revision'],
            username,
            current_item['item_type'],
            current_item['description'],
            manufactured_part_details['material'] if manufactured_part_details else None,
            fixed_part_details['vendor'] if fixed_part_details else None,
            fixed_part_details['vendor_part_number'] if fixed_part_details else None
        ))

        sql_update_item = (
            "UPDATE items SET description=?, revision=?, revisioner=? "
            "WHERE item_number=?"
        )
        cursor.execute(sql_update_item, (description, revision, username, item_number))

        con.commit()
        con.close()
        return True
    except Exception as e:
        print(f"Error updating item base in database: {e}")
        if con:
            con.rollback()
            con.close()
        return False

def update_manufactured_parts_details(item_number, description, material, revision):
    """Updates the details of a manufactured part."""
    try:
        con = get_connection()
        cursor = con.cursor()
        sql = "UPDATE manufactured_parts SET description=?, material=? WHERE item_number=?"
        cursor.execute(sql, (description, material, item_number))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(f"Error updating manufactured part details in database: {e}")
        if con:
            con.rollback()
            con.close()
        return False

def update_fixed_parts_details(item_number, description, vendor, vendor_part_number, revision):
    """Updates the details of a fixed part."""
    try:
        con = get_connection()
        cursor = con.cursor()
        sql = ("UPDATE fixed_parts SET description=?, vendor=?, "
               "vendor_part_number=? WHERE item_number=?")
        cursor.execute(sql, (description, vendor, vendor_part_number, item_number))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(f"Error updating fixed part details in database: {e}")
        if con:
            con.rollback()
            con.close()
        return False

def delete_item_by_number(item_number):
    """Deletes an item from the database."""
    sql = "DELETE FROM items WHERE item_number = ?"
    par = [item_number]
    try:
        execute(sql, par)
        return True
    except sqlite3.Error as e:
        print(f"Database error during delete: {e}")
        return False

def get_items():
    """Returns all items in the database."""
    sql = ("SELECT item_number, item_type, description, revision, creator, revisioner "
           "FROM items ORDER BY item_number")
    items = query(sql)
    return items

def get_assemblies():
    """Returns all assemblies in the database."""
    return []

def get_manufactured_parts():
    """Returns all manufactured parts in the database."""
    sql = "SELECT * FROM manufactured_parts"
    manufactured_parts = query(sql)
    return manufactured_parts

def get_fixed_parts():
    """Returns all fixed parts in the database."""
    sql = "SELECT * FROM fixed_parts"
    fixed_parts = query(sql)
    return fixed_parts

def get_items_by_user(username):
    """Returns all items created or revised by a user."""
    sql = ("SELECT item_number, item_type, description, revision, creator, revisioner "
           "FROM items WHERE creator = ? OR revisioner = ? "
           "ORDER BY item_number")
    items = query(sql, [username, username])
    return items

def get_item_revisions(item_number):
    """Returns the revision history of an item."""
    sql = """
        SELECT id, item_number, revision_number, revision_date, revisioner, 
               item_type, description, material, vendor, vendor_part_number
        FROM item_revisions 
        WHERE item_number = ? 
        ORDER BY revision_date DESC
    """
    par = [item_number]
    result = query(sql, par)
    return result
