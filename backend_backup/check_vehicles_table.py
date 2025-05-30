from app import app, db

def check_vehicles_table():
    with app.app_context():
        inspector = db.inspect(db.engine)
        
        # Check if vehicles table exists
        if 'vehicles' not in inspector.get_table_names():
            print("Error: 'vehicles' table does not exist")
            return False
            
        # Get columns in vehicles table
        columns = inspector.get_columns('vehicles')
        print("\nColumns in 'vehicles' table:")
        for col in columns:
            print(f"- {col['name']} ({col['type']})")
            
        # Check if is_available column exists
        has_is_available = any(col['name'] == 'is_available' for col in columns)
        print(f"\nHas 'is_available' column: {has_is_available}")
        
        # Check if available column exists (for backward compatibility)
        has_available = any(col['name'] == 'available' for col in columns)
        print(f"Has 'available' column: {has_available}")
        
        return True

if __name__ == "__main__":
    check_vehicles_table()
