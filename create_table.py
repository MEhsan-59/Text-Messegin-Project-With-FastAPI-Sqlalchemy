from database import engine
import models

def create_tables():
    print("Connecting to Neon.tech...")
    models.Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()