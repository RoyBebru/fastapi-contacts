from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List


from src.database.db import get_db
from src.schemas import ContactModel, ResponseContactModel
from src.repository import contacts as repository_contacts


router = APIRouter(prefix='/contacts')


@router.get("/", response_model=List[ResponseContactModel])
async def read_contacts(db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(db)
    return contacts


@router.get("/by_id/{contact_id}", response_model=ResponseContactModel)
async def read_contact_id(contact_id: int = Path(
                    description="The ID of the contact to get", ge=1),
                db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact_id(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')
    return contact


@router.get("/by_name/{contact_name}", response_model=List[ResponseContactModel])
async def read_contact_name(contact_name: str = Path(
                    description="The case insensitive name of the contact to get"),
                db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contact_name(contact_name, db)
    return contacts


@router.get("/by_lastname/{contact_lastname}",
            response_model=List[ResponseContactModel])
async def read_contact_lastname(contact_lastname: str = Path(
                    description="The case insensitive lastname of the contact to get"),
                db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contact_lastname(contact_lastname, db)
    return contacts


@router.get("/by_email/{contact_email}", response_model=ResponseContactModel)
async def read_contact_email(contact_email: str = Path(
                    description="The case insensitive email of the contact to get"),
                db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact_email(contact_email, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')
    return contact


@router.get("/birthdays_along_week", response_model=List[ResponseContactModel])
async def read_contact_birthdays_along_week(db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contact_birthdays_along_week(db)
    return contacts


@router.post("/", response_model=ResponseContactModel)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    try:
        contact = await repository_contacts.create_contact(body, db)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="ALREADY EXISTS")
    return contact


@router.put("/{contact_id}", response_model=ResponseContactModel)
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1),
                         db: Session = Depends(get_db)):
    try:
        contact = await repository_contacts.update_contact(body, contact_id, db)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="ALREADY EXISTS")
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.delete("/{contact_id}", response_model=ResponseContactModel)
async def delete_contact(contact_id: int = Path(
                description="The ID of contact to delete", ge=1),
            db: Session = Depends(get_db)):
    contact = await repository_contacts.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact
