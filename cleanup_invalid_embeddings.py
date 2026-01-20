"""
Cleanup script to remove invalid face embeddings from the database
This script identifies and removes face embeddings with incorrect dimensions
"""
import requests
import json

LARAVEL_API_URL = "http://localhost:8000"

def check_and_cleanup_embeddings():
    """Check all registered faces and identify invalid embeddings"""
    print("🔍 Fetching all registered employees...")
    
    try:
        response = requests.get(f"{LARAVEL_API_URL}/api/v1/employees/registered-faces", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch employees: {response.status_code}")
            return
        
        employees = response.json().get('data', [])
        print(f"✅ Found {len(employees)} registered employees")
        
        EXPECTED_DIM = 512
        invalid_count = 0
        valid_count = 0
        
        print("\n📊 Checking embedding dimensions...")
        print("-" * 80)
        
        for employee in employees:
            emp_id = employee.get('id')
            emp_name = employee.get('name', 'Unknown')
            emp_number = employee.get('employee_number', 'N/A')
            
            if not employee.get('face_embedding'):
                print(f"⚠️  Employee {emp_id} ({emp_name}) - No embedding found")
                continue
            
            try:
                embedding = json.loads(employee['face_embedding'])
                embedding_dim = len(embedding)
                
                if embedding_dim != EXPECTED_DIM:
                    print(f"❌ Employee {emp_id} ({emp_name} - {emp_number})")
                    print(f"   Invalid dimension: {embedding_dim} (expected {EXPECTED_DIM})")
                    print(f"   This employee needs to be re-registered!")
                    invalid_count += 1
                else:
                    valid_count += 1
                    
            except Exception as e:
                print(f"❌ Employee {emp_id} ({emp_name}) - Error parsing embedding: {e}")
                invalid_count += 1
        
        print("-" * 80)
        print(f"\n📈 Results:")
        print(f"   ✅ Valid embeddings: {valid_count}")
        print(f"   ❌ Invalid embeddings: {invalid_count}")
        
        if invalid_count > 0:
            print(f"\n⚠️  ACTION REQUIRED:")
            print(f"   {invalid_count} employee(s) have invalid face embeddings")
            print(f"   These employees need to RE-REGISTER their faces")
            print(f"   The system will skip them during face matching until re-registered")
        else:
            print(f"\n✅ All embeddings are valid! No action needed.")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Laravel backend at {LARAVEL_API_URL}")
        print("   Make sure the backend is running!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("=" * 80)
    print("🔧 Face Embedding Dimension Validator")
    print("=" * 80)
    check_and_cleanup_embeddings()
    print("\n" + "=" * 80)
