import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def main():

    # Set up database
    engine = create_engine(os.getenv("DATABASE_URL"))
    db = scoped_session(sessionmaker(bind=engine))

    # Open zips to read
    with open("zips.csv", 'r') as f:
        cities = csv.reader(f)

        # Skip header
        next(cities, None)

        # Insert each city into database
        for city in cities:
            db.execute("INSERT INTO zips (zipcode, city, state, lat, long, population) VALUES (:zipcode, :city, :state, :lat, :long, :population)",
                       {"zipcode": city[0], "city": city[1], "state": city[2], "lat": city[3], "long": city[4], "population": city[5]})

            # Indiciate when each city is imported
            print(f"Added {city[1]}")
        db.commit()


if __name__ == "__main__":
    main()
