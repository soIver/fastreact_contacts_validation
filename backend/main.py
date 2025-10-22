"""API for contact database"""
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator, Field
from sqlalchemy.orm import Session

import models, re
from db import SessionLocal

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = error['loc'][-1] if error['loc'] else 'unknown'
        msg = error['msg']
        errors.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )

# allows cross-origin requests from React
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Contact(BaseModel):
    """Contact model with validation"""
    
    id: Optional[int] = None
    first_name: str = Field(..., min_length=1, max_length=100, example="John")
    last_name: str = Field(..., min_length=1, max_length=100, example="Doe")
    company: Optional[str] = Field(None, max_length=100, example="Acme Inc")
    telephone: Optional[str] = Field(None, max_length=20, example="+1234567890")
    email: Optional[str] = Field(None, example="john@example.com")
    address: Optional[str] = Field(None, max_length=200, example="123 Main St")
    notes: Optional[str] = Field(None, max_length=500, example="Important client")

    @field_validator('first_name')
    def validate_first_name(cls, v: str) -> str:
        """Validate first name"""
        if not v or not v.strip():
            raise ValueError('First name is required')
        
        v = v.strip()
        
        if len(v) < 2:
            raise ValueError('First name must be at least 2 characters')
        
        if len(v) > 50:
            raise ValueError('First name cannot exceed 50 characters')
        
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', v):
            raise ValueError('First name can only contain Latin or Cyrillic characters')
        
        return v

    @field_validator('last_name')
    def validate_last_name(cls, v: str) -> str:
        """Validate last name"""
        if not v or not v.strip():
            raise ValueError('Last name is required')
        
        v = v.strip()
        
        if len(v) < 2:
            raise ValueError('Last name must be at least 2 characters')
        
        if len(v) > 50:
            raise ValueError('Last name cannot exceed 50 characters')
        
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', v):
            raise ValueError('Last name can only contain Latin or Cyrillic characters')
        
        return v

    @field_validator('email')
    def validate_email(cls, v):
        if v is None or v == "" or v == "NULL":
            return v
        
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, v):
            raise ValueError('Please enter a valid email address')
        
        return v

    @field_validator('telephone')
    def validate_telephone(cls, v):
        if v is None or v == "" or v == "NULL":
            return v
        
        cleaned_phone = re.sub(r'[\s\-\(\)\+]', '', v)
        
        phone_regex = r'^\d{1,16}$'
        
        if not re.match(phone_regex, cleaned_phone):
            raise ValueError('Please enter a valid phone number')
        
        return cleaned_phone

    @field_validator('notes')
    def validate_notes(cls, v):
        if v and len(v) > 500:
            raise ValueError('Notes cannot exceed 500 characters')
        return v

    class Config:
        """Pydantic config"""
        orm_mode = True


def get_db():
    """creates seperate sessions for each request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/all-contacts", response_model=List[Contact], status_code=status.HTTP_200_OK)
def get_all_contacts(db: Session = Depends(get_db)):
    """READ: Get all contacts"""
    return db.query(models.Contact).all()


@app.get(
    "/get-contact/{contact_id}", response_model=Contact, status_code=status.HTTP_200_OK
)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """READ: Get a contact by id"""
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()


@app.post(
    "/create-contact", response_model=Contact, status_code=status.HTTP_201_CREATED
)
def create_contact(contact: Contact, db: Session = Depends(get_db)):
    """CREATE: Create a new contact with validation"""
    
    # Проверка на дубликаты (упрощенная)
    db_contact = db.query(models.Contact).filter(
        models.Contact.first_name == contact.first_name,
        models.Contact.last_name == contact.last_name,
        models.Contact.email == contact.email
    ).first()

    if db_contact is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact with same name and email already exists"
        )

    new_contact = models.Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        company=contact.company,
        telephone=contact.telephone,
        email=contact.email,
        address=contact.address,
        notes=contact.notes,
    )

    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return new_contact


@app.patch(
    "/update-contact/{contact_id}",
    response_model=Contact,
    status_code=status.HTTP_200_OK,
)
def update_contact(contact_id: int, contact: Contact, db: Session = Depends(get_db)):
    """UPDATE: Update a contact with validation"""
    
    contact_to_update = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    
    if contact_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Проверка на дубликаты (исключая текущий контакт)
    duplicate_contact = db.query(models.Contact).filter(
        models.Contact.first_name == contact.first_name,
        models.Contact.last_name == contact.last_name,
        models.Contact.email == contact.email,
        models.Contact.id != contact_id
    ).first()

    if duplicate_contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another contact with same name and email already exists"
        )

    # Обновляем поля
    contact_to_update.first_name = contact.first_name
    contact_to_update.last_name = contact.last_name
    contact_to_update.company = contact.company
    contact_to_update.telephone = contact.telephone
    contact_to_update.email = contact.email
    contact_to_update.address = contact.address
    contact_to_update.notes = contact.notes

    db.commit()
    db.refresh(contact_to_update)

    return contact_to_update


@app.delete("/delete-contact/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """DELETE: Delete a contact"""
    contact_to_delete = (
        db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    )

    if contact_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="✋ Contact does not exsist"
        )

    db.delete(contact_to_delete)
    db.commit()

    return {"message": "👌 Contact deleted"}
