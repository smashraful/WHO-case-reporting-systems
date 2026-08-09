"""Seed the database with a bootstrap admin and a small location hierarchy.

Run (after ``alembic upgrade head``)::

    python -m app.scripts.seed
"""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.enums import LocationType, UserRole
from app.models.location import Location
from app.models.user import User

# Minimal Bangladesh admin hierarchy: division -> district -> upazila
LOCATION_TREE = {
    "Dhaka": {"Dhaka": ["Savar", "Dhamrai"], "Gazipur": ["Kaliakair"]},
    "Chattogram": {"Cox's Bazar": ["Ukhia", "Teknaf"]},
}


def seed_locations(db: Session) -> None:
    if db.query(Location).first():
        print("Locations already seeded; skipping.")
        return
    for division_name, districts in LOCATION_TREE.items():
        division = Location(name=division_name, type=LocationType.division)
        db.add(division)
        db.flush()
        for district_name, upazilas in districts.items():
            district = Location(
                name=district_name,
                type=LocationType.district,
                parent_id=division.id,
            )
            db.add(district)
            db.flush()
            for upazila_name in upazilas:
                db.add(
                    Location(
                        name=upazila_name,
                        type=LocationType.upazila,
                        parent_id=district.id,
                    )
                )
    db.commit()
    print("Seeded locations.")


def seed_admin(db: Session) -> None:
    email = settings.FIRST_ADMIN_EMAIL
    if db.query(User).filter(User.email == email).first():
        print(f"Admin {email} already exists; skipping.")
        return
    if not settings.FIRST_ADMIN_PASSWORD:
        print("FIRST_ADMIN_PASSWORD is empty; set it in .env to seed an admin.")
        return
    db.add(
        User(
            full_name="System Administrator",
            email=email,
            password=hash_password(settings.FIRST_ADMIN_PASSWORD),
            role=UserRole.admin,
            is_active=True,
        )
    )
    db.commit()
    print(f"Seeded admin {email}.")


def main() -> None:
    db = SessionLocal()
    try:
        seed_locations(db)
        seed_admin(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
