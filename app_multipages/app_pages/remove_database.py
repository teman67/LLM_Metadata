from sqlalchemy import create_engine, MetaData
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the PostgreSQL URL from the environment variables
POSTGRESQL_URL = os.getenv('POSTGRESQL_URL')

# Define the database engine using the PostgreSQL URL
engine = create_engine(POSTGRESQL_URL)

# Create a metadata object
metadata = MetaData()

# Reflect the tables from the database
metadata.reflect(bind=engine)

# Get the connection
with engine.connect() as connection:
    # Begin a transaction
    trans = connection.begin()
    try:
        # Loop through all tables and delete all rows
        for table in reversed(metadata.sorted_tables):
            connection.execute(table.delete())
        trans.commit()  # Commit the transaction
        print("All rows deleted successfully from all tables.")
    except Exception as e:
        trans.rollback()  # Rollback the transaction on error
        print(f"Error occurred: {e}")
