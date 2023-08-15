from datetime import date
from pydantic import BaseModel, Field, EmailStr, field_validator
import re
# from typing import List, Optional

class ResponseContactModel(BaseModel):
    id: int = Field(default=1, ge=1)
    name: str
    lastname: str
    email: str
    phone: str
    birthday: date
    note: str


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
