from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///contacts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# OpenStreetMap Nominatim API URL
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Database Configuration
Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Contact(name={self.name}, email={self.email}, subject={self.subject})>"

# SQLite Database connection string
# SQLite Database connection string
DATABASE_URL = "sqlite:///contacts.db" # Keep for local dev if env var not set, though app.config is preferred for Flask-SQLAlchemy if used
# But here we are using raw SQLAlchemy engine
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=app.config.get('DEBUG', False))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)  # Create tables if they don't exist

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/search", methods=["POST"])
def search():
    location_query = request.form.get("location")
    if not location_query:
        return redirect(url_for("home"))

    # Get latitude and longitude for the location
    location_params = {
        "q": location_query,
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    try:
        location_response = requests.get(NOMINATIM_URL, params=location_params, timeout=10)
    except requests.RequestException as e:
         return render_template("index.html", error="Error connecting to location service.")
    if location_response.status_code != 200 or not location_response.json():
        return render_template("index.html", error="Location not found. Please try again.")

    location_data = location_response.json()[0]
    lat, lon = location_data["lat"], location_data["lon"]

    # Search for cafes near the location
    overpass_query = f"""
    [out:json];
    node
      ["amenity"="cafe"]
      (around:2000,{lat},{lon});
    out;
    """
    try:
        cafe_response = requests.get(OVERPASS_URL, params={"data": overpass_query}, timeout=20)
        cafes = cafe_response.json()["elements"] if cafe_response.status_code == 200 else []
    except requests.RequestException:
        cafes = []

    return render_template("index.html", location=location_query, cafes=cafes, lat=lat, lon=lon)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        # Save the contact details to the database
        session = SessionLocal()
        try:
            new_contact = Contact(name=name, email=email, subject=subject, message=message)
            session.add(new_contact)
            session.commit()
            session.close()
            return render_template("contact.html", success=True)
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
            return render_template("contact.html", success=False)
        finally:
            session.close()

    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=os.environ.get('DEBUG', 'False') == 'True', host="0.0.0.0", port=8080)
