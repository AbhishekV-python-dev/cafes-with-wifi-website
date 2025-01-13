from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the base class for SQLAlchemy models
Base = declarative_base()

# Define the Contact model
class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Contact(name={self.name}, email={self.email}, subject={self.subject})>"

# Database connection string (SQLite uses a local file)
DATABASE_URL = "sqlite:///contact_db.sqlite3"

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the database
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # Run this script to create the tables in the database
    create_tables()
    print("SQLite database and tables created successfully!")
