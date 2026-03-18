from db_config import get_database, create_user, verify_user
import time

def test_mongodb_connection():
    print("Testing MongoDB Connection...")
    try:
        db = get_database()
        # Test by accessing a collection
        users = db['users']
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print("✗ Database connection failed:", str(e))
        return False

def test_user_operations():
    print("\nTesting User Operations...")
    
    # Test data
    test_user = {
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'testpassword123'
    }
    
    # Test user creation
    print("\n1. Creating test user...")
    success, message, user_id = create_user(
        test_user['username'],
        test_user['email'],
        test_user['password']
    )
    
    if success:
        print(f"✓ User created successfully. User ID: {user_id}")
    else:
        print(f"✗ User creation failed: {message}")
    
    # Test user verification
    if success:
        print("\n2. Verifying user login...")
        time.sleep(1)  # Small delay to ensure different timestamp
        
        login_success, user_data, login_message = verify_user(
            test_user['email'],
            test_user['password']
        )
        
        if login_success:
            print("✓ Login successful")
            print("User data:", user_data)
        else:
            print(f"✗ Login failed: {login_message}")

def main():
    print("=== MongoDB Integration Test ===\n")
    
    # Test database connection
    if test_mongodb_connection():
        # Test user operations
        test_user_operations()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 