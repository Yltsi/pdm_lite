"""
Seed script to populate the PDM Lite database with large amounts of test data.
This is used to test the application's performance with realistic data volumes.
"""
import random
import time
import sqlite3
import os
from werkzeug.security import generate_password_hash

# Configuration
DB_FILE = "database.db"
NUM_USERS = 10
NUM_MANUFACTURED_PARTS = 500
NUM_FIXED_PARTS = 500
NUM_ASSEMBLIES = 100
MAX_COMPONENTS_PER_ASSEMBLY = 20

# Test data
USERS = [f"testuser{i}" for i in range(1, NUM_USERS+1)]

MATERIALS = [
    # Metals
    "Steel", "Aluminum", "Copper", "Brass", "Titanium", "Stainless Steel", "Bronze", 
    "Cast Iron", "Zinc", "Nickel", "Tungsten", "Chrome", "Lead", "Tin", "Gold", "Silver", 
    "Platinum", "Magnesium", "Cobalt", "Molybdenum", "Beryllium", "Inconel", "Monel",

    # Plastics/Polymers
    "PVC", "ABS", "Polypropylene", "Polyethylene", "Acrylic", "Nylon", "Teflon", "PEEK",
    "Polycarbonate", "Polystyrene", "Silicone", "Delrin", "UHMW", "PTFE", "PET", "HDPE",
    "LDPE", "Polylactic Acid", "Epoxy Resin", "Acetal", "Phenolic", "Bakelite",

    # Other Materials
    "Rubber", "Carbon Fiber", "Fiberglass", "Ceramic", "Glass", "Wood", "Plywood",
    "MDF", "Particleboard", "Leather", "Foam", "Cork", "Graphite", "Diamond", "Concrete", 
    "Marble", "Granite", "Slate", "Sandstone", "Composite", "Kevlar", "Nomex",

    # Advanced Materials
    "Carbon Nanotube Composite", "Shape Memory Alloy", "High-Temperature Ceramic", 
    "Tungsten Carbide", "Boron Nitride", "Silicon Carbide", "Aerogel", "Metal Matrix Composite",
    "Synthetic Diamond", "Borosilicate Glass", "Liquid Crystal Polymer"
]

VENDORS = [
    # Large Industrial Suppliers
    "Acme Corp", "TechSupplies", "MegaParts Inc.", "Industrials Inc.", "FirstComponents", 
    "QualityParts", "GlobalSource", "McMaster-Carr", "Grainger", "MSC Industrial",
    "Fastenal", "Uline", "Digi-Key", "Mouser", "Newark", "Arrow Electronics",
    "Avnet", "Future Electronics", "TTI Inc.", "Anixter",

    # Specialized Manufacturers
    "Precision Tooling Co.", "Advanced Materials Ltd.", "Custom Components LLC", 
    "Engineered Solutions", "Tech Fabricators", "Industrial Specialties", "MicroPrecision",
    "Quantum Manufacturing", "EliteFab", "ProtoWorks", "NextGen Materials",
    "Specialty Hardware Systems", "Bespoke Engineering", "Advanced Composites Inc.",

    # Global Manufacturers
    "Siemens", "ABB", "Schneider Electric", "Honeywell", "Emerson Electric", "Parker Hannifin",
    "Bosch", "Mitsubishi Electric", "Omron", "Rockwell Automation", "GE Manufacturing",
    "Hitachi", "Panasonic Industrial", "Toshiba", "Eaton Corporation", "Phoenix Contact",

    # Regional Suppliers
    "Western Supply Co.", "Eastern Industrial", "Midwest Parts Depot", "Southern Components",
    "Pacific Rim Distributors", "Northern Manufacturing", "Atlantic Industrial Supply",
    "Mountain States Hardware", "Great Lakes Fasteners", "Central Valley Equipment",
    "Rocky Mountain Parts", "Coastal Fabricators", "Desert Industrial"
]

DESCRIPTIONS = [
    # Mechanical Components
    "Bracket", "Fastener", "Housing", "Cover", "Plate", "Gasket", "Seal", "Bearing", 
    "Shaft", "Gear", "Pulley", "Belt", "Chain", "Spring", "Screw", "Bolt", "Nut",
    "Washer", "Rivet", "Pin", "Clip", "Clamp", "Rod", "Bar", "Tube", "Pipe",
    "Hinge", "Latch", "Handle", "Knob", "Button", "Switch", "Sensor", "Motor",
    "Pump", "Valve", "Filter", "Reservoir", "Container", "Enclosure", "Mount",
    "Support", "Frame", "Chassis", "Panel", "Board", "Circuit", "Connector",

    # Detailed Mechanical Parts
    "Cam", "Follower", "Link", "Lever", "Coupler", "Bush", "Sleeve", "Spindle", "Flange",
    "Collar", "Retainer", "Spacer", "Shim", "Block", "Key", "Keyway", "Cotter", "Dowel",
    "Stud", "Eyebolt", "Grommet", "Insert", "Socket", "Sprocket", "Worm Gear", "Rack",
    "Pinion", "Clutch", "Brake", "Diaphragm", "Bellows", "O-ring", "Liner", "Piston", "Cylinder",

    # Specialized Components
    "Actuator", "Regulator", "Manifold", "Accumulator", "Exchanger", "Compressor", "Turbine",
    "Generator", "Alternator", "Transducer", "Transformer", "Capacitor", "Resistor", "Inductor",
    "Relay", "Solenoid", "Thermostat", "Thermocouple", "Potentiometer", "Encoder", "Decoder",
    "Amplifier", "Oscillator", "Controller", "Processor", "Module", "Interface", "Terminal",

    # Assembly Components
    "Sub-Assembly", "Module", "Unit", "System", "Array", "Cartridge", "Cassette", "Package",
    "Insert", "Element", "Core", "Adapter", "Fitting", "Junction", "Hub", "Base", "Plinth",
    "Skid", "Platform", "Pallet", "Carrier", "Trolley", "Harness", "Bundle", "Cluster",

    # Electronic Components
    "PCB", "IC", "CPU", "GPU", "RAM", "ROM", "EEPROM", "FPGA", "ASIC", "LED", "LCD",
    "Touchscreen", "Keyboard", "Microphone", "Speaker", "Camera", "Antenna", "Battery",
    "Charger", "Power Supply", "Inverter", "Converter", "Rectifier", "Fuse", "Breaker",
    "Cable", "Connector", "Port", "Socket", "Header", "Terminal Block"
]

ADJECTIVES = [
    # Size and Scale
    "Large", "Small", "Medium", "Tiny", "Huge", "Miniature", "Compact", "Massive", "Microscopic",
    "Oversized", "Undersized", "Full-Size", "Half-Size", "Quarter-Size", "Standard", "Custom",

    # Performance Characteristics
    "Heavy-Duty", "Lightweight", "Reinforced", "High-Performance", "Economy", "Premium",
    "Industrial", "Commercial", "Specialized", "Universal", "Multi-Purpose", "Single-Use",
    "Reusable", "Disposable", "Modular", "Integrated", "Advanced", "Basic", "Enhanced",
    "Modified", "Redesigned", "Improved", "Next-Generation", "Legacy", "Prototype", "Production",

    # Physical Properties
    "Rigid", "Flexible", "Hardened", "Tempered", "Annealed", "Heat-Treated", "Cold-Formed",
    "Cast", "Forged", "Stamped", "Machined", "Molded", "Extruded", "Welded", "Brazed",
    "Soldered", "Laminated", "Coated", "Plated", "Galvanized", "Anodized", "Enameled", 

    # Design Characteristics
    "Adjustable", "Fixed", "Portable", "Stationary", "Automated", "Manual", "Ergonomic",
    "Streamlined", "Aerodynamic", "Symmetrical", "Asymmetrical", "Balanced", "Counterbalanced",
    "Self-Aligning", "Self-Lubricating", "Self-Cleaning", "Quick-Release", "Quick-Connect",

    # Quality and Precision
    "Precision", "High-Precision", "Ultra-Precision", "Accurate", "Calibrated", "Certified",
    "Military-Spec", "Aerospace-Grade", "Medical-Grade", "Food-Grade", "Laboratory-Grade",
    "Consumer-Grade", "Professional", "Ruggedized", "Robust", "Reliable", "High-Reliability",

    # Environmental Conditions
    "Waterproof", "Dustproof", "Fireproof", "Corrosion-Resistant", "UV-Resistant", 
    "Temperature-Resistant", "Heat-Resistant", "Cold-Resistant", "Weather-Resistant",
    "Chemical-Resistant", "Impact-Resistant", "Shockproof", "Explosion-Proof", "Submersible",

    # Industry-Specific
    "Automotive", "Aerospace", "Marine", "Railway", "Agricultural", "Construction", 
    "Mining", "Petroleum", "Chemical", "Pharmaceutical", "Semiconductor", "Telecommunications",
    "Robotics", "Hydraulic", "Pneumatic", "Electrical", "Electronic", "Mechanical", "Thermal",
    "Optical", "Acoustic", "Magnetic", "Nuclear", "Renewable", "Sustainable"
]

def create_connection():
    """Create a database connection."""
    return sqlite3.connect(DB_FILE)

def clear_database():
    """Clear all existing data from the database."""
    print("Clearing existing database...")

    # Check if database exists, if not, nothing to do
    if not os.path.exists(DB_FILE):
        print("No existing database found. Creating new database.")
        return

    conn = create_connection()
    cursor = conn.cursor()

    # Drop all tables in the correct order to respect foreign key constraints
    cursor.executescript('''
    DROP TABLE IF EXISTS assemblies;
    DROP TABLE IF EXISTS manufactured_parts;
    DROP TABLE IF EXISTS fixed_parts;
    DROP TABLE IF EXISTS item_revisions;
    DROP TABLE IF EXISTS items;
    DROP TABLE IF EXISTS users;
    ''')

    conn.commit()
    conn.close()

def initialize_database():
    """Initialize the database schema by reading schema.sql."""
    print("Initializing database schema from schema.sql...")

    # Read the schema.sql file
    try:
        with open("schema.sql", "r") as f:
            schema_sql = f.read()
    except FileNotFoundError:
        print("Error: schema.sql file not found.")
        return False

    conn = create_connection()
    cursor = conn.cursor()

    # Execute the schema
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print("Database schema initialized successfully.")
        return True
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error initializing database schema: {e}")
        return False
    finally:
        conn.close()

def create_users():
    """Create test users."""
    print("Creating test users...")
    conn = create_connection()
    cursor = conn.cursor()

    for username in USERS:
        password_hash = generate_password_hash(f"password{username}")
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                      (username, password_hash))

    # Create an admin user
    admin_hash = generate_password_hash("adminpass")
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  ("admin", admin_hash))

    conn.commit()
    conn.close()
    print(f"Created {NUM_USERS+1} users")

def generate_description():
    """Generate a random part description."""
    return f"{random.choice(ADJECTIVES)} {random.choice(DESCRIPTIONS)}"

def create_manufactured_parts():
    """Create manufactured parts."""
    print("Creating manufactured parts...")
    conn = create_connection()
    cursor = conn.cursor()

    start_time = time.time()

    for i in range(NUM_MANUFACTURED_PARTS):
        # Create base item
        description = generate_description()
        creator = random.choice(USERS)
        revision = "1"
        cursor.execute(
            "INSERT INTO items (item_type, description, revision, creator, revisioner) VALUES (?, ?, ?, ?, ?)",
            ("Manufactured Part", description, revision, creator, creator)
        )
        item_number = cursor.lastrowid

        # Create manufactured part details
        material = random.choice(MATERIALS)
        cursor.execute(
            "INSERT INTO manufactured_parts (item_number, description, material, revision) VALUES (?, ?, ?, ?)",
            (item_number, description, material, revision)
        )

        # Add revision history - matching the exact schema of item_revisions
        cursor.execute(
            """
            INSERT INTO item_revisions 
            (item_number, revision_number, revisioner, item_type, description, material, vendor, vendor_part_number) 
            VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
            """,
            (item_number, revision, creator, "Manufactured Part", description, material)
        )

        if i % 100 == 0 and i > 0:
            conn.commit()
            print(f"Created {i} manufactured parts...")

    conn.commit()
    elapsed = time.time() - start_time
    print(f"Created {NUM_MANUFACTURED_PARTS} manufactured parts in {elapsed:.2f} seconds")
    conn.close()

def create_fixed_parts():
    """Create fixed parts."""
    print("Creating fixed parts...")
    conn = create_connection()
    cursor = conn.cursor()

    start_time = time.time()

    for i in range(NUM_FIXED_PARTS):
        # Create base item
        description = generate_description()
        creator = random.choice(USERS)
        revision = "1"
        cursor.execute(
            "INSERT INTO items (item_type, description, revision, creator, revisioner) VALUES (?, ?, ?, ?, ?)",
            ("Fixed Part", description, revision, creator, creator)
        )
        item_number = cursor.lastrowid

        # Create fixed part details
        vendor = random.choice(VENDORS)
        vendor_part_number = f"VP-{random.randint(10000, 99999)}"
        cursor.execute(
            "INSERT INTO fixed_parts (item_number, description, vendor, vendor_part_number, revision) VALUES (?, ?, ?, ?, ?)",
            (item_number, description, vendor, vendor_part_number, revision)
        )

        # Add revision history - matching the exact schema of item_revisions
        cursor.execute(
            """
            INSERT INTO item_revisions 
            (item_number, revision_number, revisioner, item_type, description, material, vendor, vendor_part_number) 
            VALUES (?, ?, ?, ?, ?, NULL, ?, ?)
            """,
            (item_number, revision, creator, "Fixed Part", description, vendor, vendor_part_number)
        )

        if i % 100 == 0 and i > 0:
            conn.commit()
            print(f"Created {i} fixed parts...")

    conn.commit()
    elapsed = time.time() - start_time
    print(f"Created {NUM_FIXED_PARTS} fixed parts in {elapsed:.2f} seconds")
    conn.close()

def create_assemblies():
    """Create assemblies with components."""
    print("Creating assemblies...")
    conn = create_connection()
    cursor = conn.cursor()

    start_time = time.time()

    # Get all available component IDs
    cursor.execute("SELECT item_number FROM items WHERE item_type != 'Assembly'")
    available_components = [row[0] for row in cursor.fetchall()]

    if not available_components:
        print("Error: No components available to create assemblies")
        conn.close()
        return

    for i in range(NUM_ASSEMBLIES):
        # Create base assembly item
        description = f"Assembly - {generate_description()}"
        creator = random.choice(USERS)
        revision = "1"
        cursor.execute(
            "INSERT INTO items (item_type, description, revision, creator, revisioner) VALUES (?, ?, ?, ?, ?)",
            ("Assembly", description, revision, creator, creator)
        )
        assembly_id = cursor.lastrowid

        # Add components to the assembly
        num_components = random.randint(5, MAX_COMPONENTS_PER_ASSEMBLY)
        used_components = set()

        for line in range(10, (num_components * 10) + 1, 10):  # Line numbers 10, 20, 30...
            # Ensure we don't use the same component twice in an assembly
            while True:
                component_id = random.choice(available_components)
                if component_id not in used_components and component_id != assembly_id:
                    used_components.add(component_id)
                    break

            quantity = random.randint(1, 10)
            cursor.execute(
                "INSERT INTO assemblies (assembly_item_number, component_item_number, quantity, line_number, revision) VALUES (?, ?, ?, ?, ?)",
                (assembly_id, component_id, quantity, line, revision)
            )

        # Add revision history - matching the exact schema of item_revisions
        cursor.execute(
            """
            INSERT INTO item_revisions 
            (item_number, revision_number, revisioner, item_type, description, material, vendor, vendor_part_number) 
            VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)
            """,
            (assembly_id, revision, creator, "Assembly", description)
        )

        if i % 20 == 0 and i > 0:
            conn.commit()
            print(f"Created {i} assemblies...")

    conn.commit()
    elapsed = time.time() - start_time
    print(f"Created {NUM_ASSEMBLIES} assemblies with components in {elapsed:.2f} seconds")
    conn.close()

def verify_database():
    """Verify that the database schema matches what we expect and data is populated correctly."""
    print("\nVerifying database integrity...")
    conn = create_connection()
    cursor = conn.cursor()

    # Check table counts
    tables = ["users", "items", "manufactured_parts", "fixed_parts", "assemblies", "item_revisions"]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Table '{table}' contains {count} records")

    # Check for referential integrity issues
    integrity_checks = [
        {
            "name": "Manufactured parts referential integrity",
            "query": """
                SELECT COUNT(*) FROM manufactured_parts mp 
                LEFT JOIN items i ON mp.item_number = i.item_number 
                WHERE i.item_number IS NULL
            """
        },
        {
            "name": "Fixed parts referential integrity",
            "query": """
                SELECT COUNT(*) FROM fixed_parts fp 
                LEFT JOIN items i ON fp.item_number = i.item_number 
                WHERE i.item_number IS NULL
            """
        },
        {
            "name": "Assembly components referential integrity",
            "query": """
                SELECT COUNT(*) FROM assemblies a 
                LEFT JOIN items i ON a.assembly_item_number = i.item_number 
                WHERE i.item_number IS NULL
            """
        },
        {
            "name": "Item revisions referential integrity",
            "query": """
                SELECT COUNT(*) FROM item_revisions ir 
                LEFT JOIN items i ON ir.item_number = i.item_number 
                WHERE i.item_number IS NULL
            """
        }
    ]

    for check in integrity_checks:
        cursor.execute(check["query"])
        issues = cursor.fetchone()[0]
        status = "PASS" if issues == 0 else "FAIL"
        print(f"{check['name']}: {status} ({issues} issues)")

    conn.close()

def perform_performance_tests():
    """Run a series of performance tests on the database."""
    print("\nRunning performance tests...")
    conn = create_connection()
    cursor = conn.cursor()

    tests = [
        {
            "name": "Count all items",
            "query": "SELECT COUNT(*) FROM items"
        },
        {
            "name": "Count items by type",
            "query": "SELECT item_type, COUNT(*) FROM items GROUP BY item_type"
        },
        {
            "name": "Find assemblies with most components",
            "query": """
                SELECT i.item_number, i.description, COUNT(a.component_item_number) as component_count
                FROM items i
                JOIN assemblies a ON i.item_number = a.assembly_item_number
                GROUP BY i.item_number
                ORDER BY component_count DESC
                LIMIT 10
            """
        },
        {
            "name": "Find most used components",
            "query": """
                SELECT i.item_number, i.description, COUNT(a.assembly_item_number) as usage_count
                FROM items i
                JOIN assemblies a ON i.item_number = a.component_item_number
                GROUP BY i.item_number
                ORDER BY usage_count DESC
                LIMIT 10
            """
        },
        {
            "name": "Complex join with filtering",
            "query": """
                SELECT i.item_number, i.description, i.revision, mp.material
                FROM items i
                JOIN manufactured_parts mp ON i.item_number = mp.item_number
                WHERE mp.material = 'Steel'
                LIMIT 100
            """
        },
        {
            "name": "Search by description (without index)",
            "query": "SELECT * FROM items WHERE description LIKE '%Bracket%' LIMIT 100"
        },
        {
            "name": "Get user contribution statistics",
            "query": """
                SELECT creator, COUNT(*) as item_count
                FROM items
                GROUP BY creator
                ORDER BY item_count DESC
            """
        }
    ]

    results = []

    for test in tests:
        start_time = time.time()
        cursor.execute(test["query"])
        data = cursor.fetchall()
        elapsed = time.time() - start_time

        results.append({
            "name": test["name"],
            "time": elapsed,
            "rows": len(data)
        })

        print(f"{test['name']}: {elapsed:.4f} seconds, {len(data)} rows returned")

    conn.close()

    # Save results to a file
    with open("performance_results.txt", "w") as f:
        f.write("PDM Lite Performance Test Results\n")
        f.write("================================\n\n")
        f.write(f"Database size: {os.path.getsize(DB_FILE) / (1024 * 1024):.2f} MB\n")
        f.write(f"Total items: {NUM_MANUFACTURED_PARTS + NUM_FIXED_PARTS + NUM_ASSEMBLIES}\n\n")

        for result in results:
            f.write(f"{result['name']}:\n")
            f.write(f"  Time: {result['time']:.4f} seconds\n")
            f.write(f"  Rows: {result['rows']}\n\n")

    print(f"Performance results saved to performance_results.txt")

def main():
    """Main function to run the seeding process."""
    print("PDM Lite Database Seeder")
    print("=======================")

    # Confirm before proceeding
    response = input("This will clear the existing database and create test data. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        return

    start_time = time.time()

    # Run the seeding process
    clear_database()
    if not initialize_database():
        print("Failed to initialize database schema. Aborting.")
        return

    create_users()
    create_manufactured_parts()
    create_fixed_parts()
    create_assemblies()

    # Verify database integrity
    verify_database()

    # Run performance tests
    perform_performance_tests()

    total_time = time.time() - start_time
    print(f"\nSeeding completed in {total_time:.2f} seconds.")
    print(f"Created {NUM_USERS} users, {NUM_MANUFACTURED_PARTS} manufactured parts, {NUM_FIXED_PARTS} fixed parts, and {NUM_ASSEMBLIES} assemblies.")

if __name__ == "__main__":
    main()
