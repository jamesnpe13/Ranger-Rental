"""Script to update the vehicles table with owner_id"""
from app import app, db
from models.vehicle import Vehicle
from sqlalchemy import text

def update_vehicles_table():
    with app.app_context():
        try:
            # Check if owner_id column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('vehicles')]
            
            if 'owner_id' not in columns:
                # Add owner_id to existing vehicles (default to 1 for the first user)
                db.session.execute(text("""
                    ALTER TABLE vehicles 
                    ADD COLUMN owner_id INTEGER NOT NULL DEFAULT 1
                    REFERENCES users(id) ON DELETE CASCADE
                """))
                db.session.commit()
                print("Successfully added owner_id to vehicles table")
            else:
                print("owner_id column already exists in vehicles table")
                
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating vehicles table: {str(e)}")
            return False

if __name__ == "__main__":
    update_vehicles_table()
