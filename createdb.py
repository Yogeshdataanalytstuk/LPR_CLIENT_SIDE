from app import app, db, User, NumberPlate  
def create_database():
    with app.app_context():
        db.create_all()
        print("Database created successfully.")

        # Add initial user
        username = input("Enter username for the initial user: ")
        password = input("Enter password for the initial user: ")

        if username and password:
            # Check if the user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"User '{username}' already exists.")
            else:
                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()
                print(f"User '{username}' created successfully.")
        else:
            print("Username and password cannot be empty.")

if __name__ == '__main__':
    create_database()
