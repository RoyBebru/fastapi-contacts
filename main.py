from datetime import date, timedelta
from fastapi import FastAPI, Request, Path, Query, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator, EmailStr
import re
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import time


from db import get_db, Contact


app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


class ResponseContactModel(BaseModel):
    id: int = Field(default=1, ge=1)
    name: str
    lastname: str
    email: str
    phone: str
    birthday: date
    note: str


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Здійснюємо запит
        result = db.execute("SELECT 1").fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/contacts")
async def read_contacts(db: Session = Depends(get_db)) -> \
        list[ResponseContactModel]:
    contacts = db.query(Contact).all()
    return contacts


@app.get("/contacts/by_id/{contact_id}", response_model=ResponseContactModel)
async def read_contact_id(contact_id: int = Path(description="The ID of the contact to get", ge=1),
                    db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')
    return contact


@app.get("/contacts/by_name/{contact_name}")
async def read_contact_name(contact_name: str = Path(description="The case insensitive name of the contact to get"),
                    db: Session = Depends(get_db)):
    contacts = db.query(Contact).filter(func.lower(Contact.name) == func.lower(contact_name)).all()
    return contacts


@app.get("/contacts/by_lastname/{contact_lastname}")
async def read_contact_lastname(contact_lastname: str = Path(description="The case insensitive lastname of the contact to get"),
                    db: Session = Depends(get_db)):
    contacts = db.query(Contact).filter(func.lower(Contact.lastname) == func.lower(contact_lastname)).all()
    return contacts


@app.get("/contacts/by_email/{contact_email}")
async def read_contact_email(contact_email: str = Path(description="The case insensitive email of the contact to get"),
                    db: Session = Depends(get_db)):
    contacts = db.query(Contact).filter(func.lower(Contact.email) == func.lower(contact_email)).all()
    return contacts


def get_birthday_per_week(users: list):

    today = date.today()
    # today = date(2023,2,28)


@app.get("/contacts/birthdays_along_week")
async def read_contacts_birthdays_along_week(db: Session = Depends(get_db)) -> \
        list[ResponseContactModel]:
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


class ContactModel(BaseModel):
    name: str
    lastname: str
    email: EmailStr
    phone: str
    birthday: date
    note: str

    @field_validator("phone")
    @classmethod
    def adopt_phone(cls, v: str):
        pattern_phone =  r"^(?:\+\d{1,3})?\s*(?:\(\d{2,5}\)|\d{2,5})?" \
                         r"\s*\d{1,3}(?:\s*-)?\s*\d{1,3}(?:\s*-)?\s*\d{1,3}\s*$"
        v = " ".join(v.split())
        v = v.replace(" - ", "-").replace(" -", "-").replace("- ", "-")
        if not re.search(pattern_phone, v):
            raise ValueError(f"Wrong phone number '{v}'")
        return v


@app.post("/contacts")
async def create_contact(contact: ContactModel, db: Session = Depends(get_db)):
    new_contact = Contact(name=contact.name,
                          lastname=contact.lastname,
                          email=contact.email,
                          phone=contact.phone,
                          birthday=contact.birthday,
                          note=contact.note)
    db.add(new_contact)
    try:
        db.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="ALREADY EXISTS")
    db.refresh(new_contact)
    return new_contact


@app.put("/contacts/{contact_id}", response_model=ResponseContactModel)
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    contact.name = body.name
    contact.lastname = body.lastname
    contact.email = body.email
    contact.phone = body.phone
    contact.birthday = body.birthday
    contact.note = body.note
    db.commit()
    return contact


@app.delete("/contacts/{contact_id}", response_model=ResponseContactModel)
async def delete_contact(contact_id: int = Path(description="The ID of contact to delete", ge=1),
            db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    db.delete(contact)
    db.commit()
    return contact
