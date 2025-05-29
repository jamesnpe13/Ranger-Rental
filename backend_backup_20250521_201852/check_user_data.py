import sqlite3

def check_user_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('instance/test.db')  # Update the path if needed
    cursor = conn.cursor()
    
    # Fetch all users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    # Get column names
    columns = [description[0] for description in cursor.description]
    
    print("Users in database:")
    for user in users:
        user_data = dict(zip(columns, user))
        print(f"ID: {user_data['id']}")
        print(f"Email: {user_data['email']}")
        print(f"First Name: {user_data['first_name']}")
        print(f"Last Name: {user_data['last_name']}")
        print(f"Role: {user_data['role']}")
        print(f"Password Hash: {user_data['password_hash']}")
        print("-" * 50)
    
    conn.close()

if __name__ == '__main__':
    check_user_data()
