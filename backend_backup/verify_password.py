from flask_bcrypt import Bcrypt

# The stored hash from the database
stored_hash = "$2b$12$G6kNbCHiB2bw9NmUZmq1H.4otVLjY8obrDT/9hKn1CFOjgEmH5aRy"
password_to_check = "admin123"

# Initialize Bcrypt
bcrypt = Bcrypt()

# Verify the password
result = bcrypt.check_password_hash(stored_hash, password_to_check)

print(f"Password verification result: {result}")
print(f"Stored hash: {stored_hash}")
print(f"Password to check: {password_to_check}")

# Generate a new hash for comparison
new_hash = bcrypt.generate_password_hash(password_to_check).decode('utf-8')
print(f"Newly generated hash: {new_hash}")
print(f"New hash matches stored hash: {new_hash == stored_hash}")
print(f"New hash verification: {bcrypt.check_password_hash(new_hash, password_to_check)}")
