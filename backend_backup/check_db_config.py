from app import app, db

def check_database_config():
    with app.app_context():
        print("=== Database Configuration ===")
        print(f"SQLAlchemy Database URL: {db.engine.url}")
        print(f"Database Driver: {db.engine.driver}")
        print(f"Database Name: {db.engine.url.database}")
        print(f"Database Location: {db.engine.url}")
        
        # Try to connect to the database
        try:
            connection = db.engine.connect()
            print("\n=== Database Connection Successful ===")
            print("Database connection test passed!")
            connection.close()
            return True
        except Exception as e:
            print("\n=== Database Connection Failed ===")
            print(f"Error: {str(e)}")
            return False

if __name__ == "__main__":
    check_database_config()
