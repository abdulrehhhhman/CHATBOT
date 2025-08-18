#!/usr/bin/env python3

"""
Database setup script for LMS Chatbot
This script creates all tables and sets up the database schema
"""

import os
import sys
from pathlib import Path
from sqlalchemy import text

# Import database configuration
from database.config import engine, Base, test_db_connection, SessionLocal

# Import all models to ensure they're registered with Base
from models.user import User
from models.chat import Chat
from models.course import Course, CourseEnrollment, CourseMaterial

def verify_user_model():
    """Verify that the User model has the correct columns"""
    try:
        print("🔍 Verifying User model structure...")
        
        # Check if User model has hashed_password attribute
        if hasattr(User, 'hashed_password'):
            print("✅ User model has 'hashed_password' column")
        else:
            print("❌ User model missing 'hashed_password' column")
            return False
            
        # Print all columns
        print("📋 User model columns:")
        for column in User.__table__.columns:
            print(f"   - {column.name}: {column.type}")
            
        return True
    except Exception as e:
        print(f"❌ Error verifying User model: {str(e)}")
        return False

def drop_tables_with_cascade():
    """Drop all existing tables with CASCADE to handle foreign keys"""
    try:
        print("🗑️  Dropping existing tables with CASCADE...")
        
        with engine.connect() as connection:
            # Start a transaction
            trans = connection.begin()
            try:
                # Get all table names in the public schema
                result = connection.execute(text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                """))
                
                tables = result.fetchall()
                
                if tables:
                    # Drop each table with CASCADE
                    for table in tables:
                        table_name = table[0]
                        print(f"   Dropping table: {table_name}")
                        connection.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                    
                    print("✅ All tables dropped successfully!")
                else:
                    print("ℹ️  No tables found to drop")
                
                trans.commit()
                
            except Exception as e:
                trans.rollback()
                raise e
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to drop tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_tables():
    """Create all database tables"""
    try:
        print("🔄 Creating database tables...")
        
        # Verify models first
        if not verify_user_model():
            return False
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        
        # Verify tables were created
        print("\n📋 Verifying created tables:")
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            
            tables = result.fetchall()
            for table in tables:
                print(f"   ✓ {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def recreate_tables():
    """Drop and recreate all tables - USE WITH CAUTION!"""
    print("⚠️  WARNING: This will delete ALL existing data!")
    print("🔄 Recreating database schema...")
    
    if drop_tables_with_cascade():
        return create_tables()
    return False

def verify_database_schema():
    """Verify the database schema was created correctly"""
    try:
        print("🔍 Verifying database schema...")
        
        with engine.connect() as connection:
            # Check users table structure
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            
            if not columns:
                print("❌ Users table not found!")
                return False
            
            print("📋 Users table schema:")
            hashed_password_exists = False
            
            for column_name, data_type, is_nullable in columns:
                nullable_str = "NULL" if is_nullable == "YES" else "NOT NULL"
                print(f"   - {column_name}: {data_type} ({nullable_str})")
                if column_name == 'hashed_password':
                    hashed_password_exists = True
            
            if hashed_password_exists:
                print("✅ Database schema is correct!")
                return True
            else:
                print("❌ hashed_password column missing in database!")
                return False
                
    except Exception as e:
        print(f"❌ Error verifying database schema: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_data():
    """Create some sample data for testing"""
    # First verify the schema is correct
    if not verify_database_schema():
        print("❌ Skipping sample data creation due to schema issues")
        return False
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            print("📝 Sample data already exists")
            return True
            
        print("🔄 Creating sample data...")
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=User.get_password_hash("admin123"),
            full_name="System Administrator", 
            role="admin"
        )
        db.add(admin_user)
        
        # Create sample instructor
        instructor = User(
            email="instructor@example.com",
            username="instructor",
            hashed_password=User.get_password_hash("instructor123"),
            full_name="John Instructor",
            role="instructor"
        )
        db.add(instructor)
        
        # Create sample student
        student = User(
            email="student@example.com", 
            username="student",
            hashed_password=User.get_password_hash("student123"),
            full_name="Jane Student",
            role="student"
        )
        db.add(student)
        
        db.commit()
        
        # Get the instructor ID after commit
        db.refresh(instructor)
        
        # Create sample course
        course = Course(
            title="Introduction to Computer Science",
            description="Basic concepts of programming and computer science",
            course_code="CS101",
            instructor_id=instructor.id,
            semester="Fall 2024"
        )
        db.add(course)
        
        db.commit()
        db.refresh(course)
        
        # Enroll student in course
        enrollment = CourseEnrollment(
            user_id=student.id,
            course_id=course.id
        )
        db.add(enrollment)
        
        db.commit()
        
        print("✅ Sample data created!")
        print("\n👤 Test Users:")
        print("   - admin@example.com / admin123 (Admin)")
        print("   - instructor@example.com / instructor123 (Instructor)")  
        print("   - student@example.com / student123 (Student)")
        print("\n📚 Sample Course: CS101 - Introduction to Computer Science")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample data creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

def test_user_operations():
    """Test basic user operations to verify everything works"""
    try:
        print("🧪 Testing user operations...")
        
        db = SessionLocal()
        
        # Test querying a user
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        
        if admin_user:
            print(f"✅ Successfully queried user: {admin_user.username}")
            
            # Test password verification
            if admin_user.verify_password("admin123"):
                print("✅ Password verification works")
            else:
                print("❌ Password verification failed")
                return False
                
            # Test password hashing
            test_hash = User.get_password_hash("test123")
            if test_hash and len(test_hash) > 10:
                print("✅ Password hashing works")
            else:
                print("❌ Password hashing failed")
                return False
                
            print("✅ All user operations working correctly!")
            return True
        else:
            print("❌ Could not find test user")
            return False
            
    except Exception as e:
        print(f"❌ User operations test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

def main():
    """Main setup function"""
    print("🚀 Starting LMS Chatbot Database Setup...")
    print("=" * 50)
    
    # Test database connection first
    print("🔍 Testing database connection...")
    conn_result = test_db_connection()
    
    if conn_result["status"] == "error":
        print(f"❌ Database connection failed: {conn_result['message']}")
        return False
        
    print("✅ Database connection successful!")
    print(f"📊 PostgreSQL Version: {conn_result.get('postgresql_version', 'Unknown')}")
    print()
    
    # Recreate tables to fix schema issues
    print("🔄 Recreating tables to fix schema issues...")
    
    success = recreate_tables()
    
    if not success:
        print("❌ Failed to recreate tables!")
        return False
    
    print()
    
    # Verify schema
    if not verify_database_schema():
        print("❌ Schema verification failed!")
        return False
    
    print()
    
    # Create sample data
    if not create_sample_data():
        print("❌ Failed to create sample data!")
        return False
        
    print()
    
    # Test user operations
    if not test_user_operations():
        print("❌ User operations test failed!")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Database setup completed successfully!")
    print("\n🔗 Next steps:")
    print("1. Check pgAdmin to see the new tables")
    print("2. Test user registration: http://localhost:8000/docs")
    print("3. Test: http://localhost:8000/test-gemini")
    print("4. Try registering a user via the API")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Database setup failed! Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Database setup completed successfully!")