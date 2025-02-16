DROP TABLE IF EXISTS assemblies;
DROP TABLE IF EXISTS manufactured_parts;
DROP TABLE IF EXISTS fixed_parts;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE IF NOT EXISTS items (
    item_number INTEGER PRIMARY KEY,
    item_type TEXT NOT NULL,
    description TEXT,
    revision TEXT DEFAULT 'A',
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creator TEXT,
    revisioner TEXT
);

CREATE TABLE IF NOT EXISTS manufactured_parts (
    item_number INTEGER PRIMARY KEY,
    description TEXT,
    material TEXT,
    revision TEXT DEFAULT 'A',
    FOREIGN KEY (item_number) REFERENCES items(item_number)
);

CREATE TABLE IF NOT EXISTS fixed_parts (
    item_number INTEGER PRIMARY KEY,
    description TEXT,
    vendor TEXT,
    vendor_part_number TEXT,
    revision TEXT DEFAULT 'A',
    FOREIGN KEY (item_number) REFERENCES items(item_number)
);

CREATE TABLE IF NOT EXISTS assemblies (
    assembly_item_number INTEGER,
    component_item_number INTEGER,
    quantity INTEGER NOT NULL DEFAULT 1,
    revision TEXT DEFAULT 'A',
    PRIMARY KEY (assembly_item_number, component_item_number),
    FOREIGN KEY (assembly_item_number) REFERENCES items(item_number),
    FOREIGN KEY (component_item_number) REFERENCES items(item_number)
);
