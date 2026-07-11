from uuid import UUID
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.organization import Organization
from app.models.hcp import HealthcareProfessional
from app.models.user import User


def seed_data() -> None:
    db: Session = SessionLocal()
    try:
        print("Seeding database...")
        
        # 1. Seed Organizations
        orgs_data = [
            {
                "id": UUID("b0000000-0000-0000-0000-000000000001"),
                "name": "City Heart Institute",
                "organization_type": "Hospital",
                "city": "Lahore",
                "state": "Punjab",
                "country": "Pakistan",
            },
            {
                "id": UUID("b0000000-0000-0000-0000-000000000002"),
                "name": "MedCare Hospital",
                "organization_type": "Hospital",
                "city": "Karachi",
                "state": "Sindh",
                "country": "Pakistan",
            },
            {
                "id": UUID("b0000000-0000-0000-0000-000000000003"),
                "name": "Wellness Clinic",
                "organization_type": "Clinic",
                "city": "Islamabad",
                "state": "ICT",
                "country": "Pakistan",
            },
        ]
        
        for org in orgs_data:
            existing = db.query(Organization).filter(Organization.id == org["id"]).first()
            if not existing:
                new_org = Organization(**org)
                db.add(new_org)
                print(f"Created organization: {org['name']}")
                
        db.commit()

        # 2. Seed Healthcare Professionals (HCPs)
        hcps_data = [
            {
                "id": UUID("a0000000-0000-0000-0000-000000000001"),
                "organization_id": UUID("b0000000-0000-0000-0000-000000000001"),
                "first_name": "Sarah",
                "last_name": "Khan",
                "specialty": "Cardiology",
                "phone": "+923001234567",
                "email": "sarah.khan@cityheart.org",
                "preferred_channel": "In-person",
            },
            {
                "id": UUID("a0000000-0000-0000-0000-000000000002"),
                "organization_id": UUID("b0000000-0000-0000-0000-000000000002"),
                "first_name": "Ali",
                "last_name": "Raza",
                "specialty": "Internal Medicine",
                "phone": "+923007654321",
                "email": "ali.raza@medcare.org",
                "preferred_channel": "Call",
            },
            {
                "id": UUID("a0000000-0000-0000-0000-000000000003"),
                "organization_id": UUID("b0000000-0000-0000-0000-000000000003"),
                "first_name": "Maryam",
                "last_name": "Nadeem",
                "specialty": "Endocrinology",
                "phone": "+923009876543",
                "email": "maryam.nadeem@wellness.org",
                "preferred_channel": "Video",
            },
        ]

        for hcp in hcps_data:
            existing = db.query(HealthcareProfessional).filter(HealthcareProfessional.id == hcp["id"]).first()
            if not existing:
                new_hcp = HealthcareProfessional(**hcp)
                db.add(new_hcp)
                print(f"Created HCP: Dr. {hcp['first_name']} {hcp['last_name']}")
                
        db.commit()

        # 3. Seed Default User (sales representative)
        default_user_id = UUID("c0000000-0000-0000-0000-000000000001")
        existing_user = db.query(User).filter(User.id == default_user_id).first()
        if not existing_user:
            user = User(
                id=default_user_id,
                full_name="CRM Demo Sales Rep",
                email="rep@crmdemo.com",
                role="Representative",
                territory="North Region",
            )
            db.add(user)
            print("Created default sales representative user.")
            db.commit()

        print("Database seeding completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
