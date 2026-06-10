from app import create_app, db
from app.seeds import seed_database

app = create_app()

with app.app_context():
    db.create_all()
    seed_database()
    print("Database initialized and seeded successfully.")
