"""
Create a test user account for testing the application.
"""
from app import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    # Check if test user already exists
    existing_user = User.query.filter_by(username='testteacher').first()

    if existing_user:
        print("[INFO] Test user already exists")
        print(f"Username: {existing_user.username}")
        print(f"Email: {existing_user.email}")
        print(f"Reputation: {existing_user.reputation_score}")
    else:
        # Create test user
        test_user = User(
            username='testteacher',
            email='teacher@test.com',
            display_name='Test Teacher',
            bio='I am a test teacher exploring this amazing platform!',
            school='Test Elementary School',
            grade_level='Elementary',
            subjects_taught='Math, Science, English',
            years_teaching=5,
            location='Test City, TS',
            about_me='Passionate about education and technology.',
            teaching_philosophy='Every student can succeed with the right support.',
            profile_public=True,
            show_favorites_public=True
        )
        test_user.set_password('password123')

        db.session.add(test_user)
        db.session.commit()

        print("[OK] Test user created successfully!")
        print(f"Username: testteacher")
        print(f"Password: password123")
        print(f"Email: teacher@test.com")
        print(f"\nYou can now log in at: http://127.0.0.1:5000/login")

    # Create a second test user for social features testing
    existing_user2 = User.query.filter_by(username='teacherjane').first()

    if not existing_user2:
        test_user2 = User(
            username='teacherjane',
            email='jane@test.com',
            display_name='Jane Educator',
            bio='Experienced teacher sharing great resources!',
            school='Lincoln High School',
            grade_level='High School',
            subjects_taught='English, History',
            years_teaching=10,
            location='Springfield, IL',
            profile_public=True,
            reputation_score=150,  # Give some reputation
            total_reviews=5,
            total_submissions=3
        )
        test_user2.set_password('password123')
        db.session.add(test_user2)
        db.session.commit()
        print("\n[OK] Second test user 'teacherjane' created for social testing!")

    # Show all users
    all_users = User.query.all()
    print(f"\n[INFO] Total users in database: {len(all_users)}")
