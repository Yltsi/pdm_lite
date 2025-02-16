import sqlite3
from flask import g

def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

def last_insert_id():
    return g.last_insert_id    
    
def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result

def add_item_base(item_type, description, revision, creator):
    sql = "insert into items (item_type, description, revision, creator) values (?, ?, ?, ?)"
    par = [item_type, description, revision, creator]
    execute(sql, par)
    item_number = last_insert_id()
    return item_number

def add_manufactured_parts_details(item_number, description, material, revision="A"):
    sql = "insert into manufactured_parts (item_number, description, material, revision) values (?, ?, ?, ?)"
    par = [item_number, description, material, revision]
    execute(sql, par)
    return True

def add_fixed_part_details(item_number, description, vendor, vendor_part_number, revision="A"):
    sql = "insert into fixed_parts (item_number, description, vendor, vendor_part_number, revision) values (?, ?, ?, ?, ?)"
    par = [item_number, description, vendor, vendor_part_number, revision]
    execute(sql, par)
    return True

def get_item_by_number(item_number):
    sql = "select * from items where item_number = ?"
    par = [item_number]
    result = query(sql, par)
    if result:
        return result[0]
    return None

def search_items_db(search_description, item_filter):
    sql = "SELECT item_number, item_type, description, revision, creator, revisioner FROM items WHERE 1=1"
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
    sql = "SELECT item_number, item_type, description, revision FROM items ORDER BY item_number"
    items = query(sql)
    print("get_all_items_ordered_by_number items:", items)
    return items

def get_manufactured_part_details(item_number):
    sql = "SELECT * FROM manufactured_parts WHERE item_number = ?"
    par = [item_number]
    result = query(sql, par)
    if result:
        return result[0]
    return None

def get_fixed_part_details(item_number):
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

        sql_update_item = "UPDATE items SET description=?, revision=?, revisioner=? WHERE item_number=?"
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
    try:
        con = get_connection()
        cursor = con.cursor()
        sql = "UPDATE fixed_parts SET description=?, vendor=?, vendor_part_number=? WHERE item_number=?"
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
    sql = "DELETE FROM items WHERE item_number = ?"
    par = [item_number]
    try:
        execute(sql, par)
        return True
    except sqlite3.Error as e:
        print(f"Database error during delete: {e}")
        return False
    
def get_items():
    sql = "SELECT item_number, item_type, description, revision, creator, revisioner FROM items ORDER BY item_number"
    items = query(sql)
    return items

def get_assemblies():
    return []

def get_manufactured_parts():
    sql = "SELECT * FROM manufactured_parts"
    manufactured_parts = query(sql)
    return manufactured_parts

def get_fixed_parts():
    sql = "SELECT * FROM fixed_parts"
    fixed_parts = query(sql)
    return fixed_parts