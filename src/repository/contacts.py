from datetime import date, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List


from src.database.models import Contact
from src.schemas import ContactModel


async def get_contacts(db: Session) -> List[Contact]:
    return db.query(Contact).all()


async def get_contact_id(contact_id: int, db: Session) -> Contact:
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def get_contact_name(contact_name: str, db: Session) -> List[Contact]:
    return db.query(Contact).filter(
                func.lower(Contact.name) == func.lower(contact_name)).all()


async def get_contact_lastname(contact_lastname: str, db: Session) -> List[Contact]:
    return db.query(Contact).filter(
                func.lower(Contact.lastname) == func.lower(contact_lastname)).all()


async def get_contact_email(contact_email: str, db: Session) -> Contact:
    return db.query(Contact).filter(
                func.lower(Contact.email) == func.lower(contact_email)).first()


async def get_contact_birthdays_along_week(db: Session) -> List[Contact]:
    contacts = db.query(Contact).all()
    searched_contacts = []

    today = date.today()
    date_shift = timedelta(0)
    today_over_week = today + timedelta(days=7)

    # Period must be in the same year. Otherwise shift dates on 2 weeks
    if today.year < today_over_week.year:
        # The years in both dates must be the same
        date_shift = timedelta(days=14)
        today -= date_shift
        today_over_week -= date_shift

    # Searching appropriate birthdays
    for contact in contacts:
        bday = contact.birthday - date_shift

        try:
            bday = bday.replace(year=today.year)
        except ValueError:
            # Maybe shifted birthday on February, 29 -> March, 1
            bday += timedelta(days=1)
            bday = bday.replace(year=today.year)

        if today <= bday < today_over_week:
            searched_contacts.append(contact)
    return searched_contacts


async def create_contact(body: ContactModel, db: Session) -> Contact:
    contact = Contact(name=body.name,
                      lastname=body.lastname,
                      email=body.email,
                      phone=body.phone,
                      birthday=body.birthday,
                      note=body.note)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactModel, contact_id: int, db: Session) \
        -> Contact | None:
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        contact.name = body.name
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.note = body.note
        db.commit()
    return contact


async def delete_contact(contact_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact
