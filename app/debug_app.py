# Complete debug script - save as debug_app.py
# Run this to identify all issues in your application

import os
import sys
import traceback
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check all required environment variables"""
    print("🔍 Checking Environment Variables...")
    
    required_vars = [
        "DATABASE_URL",
        "GOOGLE_API_KEY", 
        "PINECONE_API_KEY",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show partial key for security
            if "KEY" in var:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: NOT SET")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def check_database_connection():
    """Test database connection"""
    print("\n🔍 Checking Database Connection...")
    
    try:
        from database.config import test_db_connection
        result = test_db_connection()
        
        if result["status"] == "success":
            print("  ✅ Database connection successful")
            print(f"  📊 PostgreSQL Version: {result.get('postgresql_version', 'Unknown')}")
            return True
        else:
            print(f"  ❌ Database connection failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"  ❌ Database connection error: {str(e)}")
        return False

def check_required_packages():
    """Check if all required packages are installed"""
    print("\n🔍 Checking Required Packages...")
    
    required_packages = {
        'fastapi': 'FastAPI framework',
        'sqlalchemy': 'Database ORM',
        'psycopg2': 'PostgreSQL adapter',
        'python-multipart': 'File upload support',
        'google-generativeai': 'Gemini AI',
        'pinecone': 'Vector database',
        'PyPDF2': 'PDF processing',
        'python-docx': 'Word document processing',
        'uvicorn': 'ASGI server'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}: {description}")
        except ImportError:
            print(f"  ❌ {package}: {description} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_models():
    """Check if database models are properly defined"""
    print("\n🔍 Checking Database Models...")
    
    try:
        from models.user import User
        from models.chat import Chat
        from models.course import Course, CourseMaterial
        
        # Check User model
        user_attrs = ['email', 'username', 'hashed_password', 'full_name', 'role']
        for attr in user_attrs:
            if hasattr(User, attr):
                print(f"  ✅ User.{attr}")
            else:
                print(f"  ❌ User.{attr} - MISSING")
        
        # Check CourseMaterial model
        material_attrs = ['title', 'content', 'file_type', 'course_id']
        for attr in material_attrs:
            if hasattr(CourseMaterial, attr):
                print(f"  ✅ CourseMaterial.{attr}")
            else:
                print(f"  ❌ CourseMaterial.{attr} - MISSING")
        
        # Check Chat model
        chat_attrs = ['user_id', 'message', 'response']
        for attr in chat_attrs:
            if hasattr(Chat, attr):
                print(f"  ✅ Chat.{attr}")
            else:
                print(f"  ❌ Chat.{attr} - MISSING")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Model import error: {str(e)}")
        return False

def test_gemini_api():
    """Test Gemini API connection"""
    print("\n🔍 Testing Gemini API...")
    
    try:
        import google.generativeai as genai
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print("  ❌ GOOGLE_API_KEY not set")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content("Say 'API test successful' in exactly those words")
        
        if response and response.text:
            print(f"  ✅ Gemini API working - Response: {response.text.strip()}")
            return True
        else:
            print("  ❌ Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"  ❌ Gemini API error: {str(e)}")
        return False

def test_pinecone_api():
    """Test Pinecone API connection"""
    print("\n🔍 Testing Pinecone API...")
    
    try:
        from pinecone import Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        
        if not api_key:
            print("  ❌ PINECONE_API_KEY not set")
            return False
        
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()
        
        if indexes:
            index_names = [idx['name'] for idx in indexes.get('indexes', [])]
            print(f"  ✅ Pinecone API working - Found {len(index_names)} indexes")
            if index_names:
                print(f"      Indexes: {', '.join(index_names)}")
        else:
            print("  ✅ Pinecone API working - No indexes found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Pinecone API error: {str(e)}")
        return False

def check_routes():
    """Check if routes are properly configured"""
    print("\n🔍 Checking Route Files...")
    
    route_files = [
        'api/routes/auth.py',
        'api/routes/chat.py', 
        'api/routes/courses.py'
    ]
    
    all_exist = True
    
    for route_file in route_files:
        if os.path.exists(route_file):
            print(f"  ✅ {route_file}")
        else:
            print(f"  ❌ {route_file} - FILE MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Main debug function"""
    print("🚀 LMS RAG Application Debug Report")
    print("=" * 50)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Required Packages", check_required_packages),
        ("Database Connection", check_database_connection),
        ("Database Models", check_models),
        ("Route Files", check_routes),
        ("Gemini API", test_gemini_api),
        ("Pinecone API", test_pinecone_api)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"  ❌ {check_name} check failed: {str(e)}")
            results[check_name] = False
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\n🎯 Overall Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your application should be working.")
    else:
        print("\n⚠️  Issues found. Fix the failed checks above.")
        print("\n🔧 Common Solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check your .env file has all required variables")
        print("3. Run: python setup_database.py")
        print("4. Verify your API keys are correct")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)