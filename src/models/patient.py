from src.models.user import db
from datetime import datetime

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    parent_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    patient_phone = db.Column(db.String(20))  # Patient's own phone number
    
    # Address components
    city = db.Column(db.String(100))
    area = db.Column(db.String(100))
    street = db.Column(db.String(100))
    apartment = db.Column(db.String(50))
    
    blood_type = db.Column(db.String(5))
    allergies = db.Column(db.Text)  # JSON string for multiple allergies
    medical_history = db.Column(db.Text)
    
    # New fields for visit management
    visit_datetime = db.Column(db.DateTime)  # When patient came to clinic
    visit_type = db.Column(db.String(50))  # examination, fast examination, consultation
    hall_status = db.Column(db.String(20), default='Out')  # In, Out
    doctor_comments = db.Column(db.Text)
    status = db.Column(db.String(50), default='waiting')  # waiting, in_hall, finished
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_full_address(self):
        """Return address as a sentence"""
        address_parts = []
        if self.apartment:
            address_parts.append(f"Apartment {self.apartment}")
        if self.street:
            address_parts.append(self.street)
        if self.area:
            address_parts.append(self.area)
        if self.city:
            address_parts.append(self.city)
        return ", ".join(address_parts) if address_parts else ""
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'parent_name': self.parent_name,
            'phone': self.phone,
            'patient_phone': self.patient_phone,
            'city': self.city,
            'area': self.area,
            'street': self.street,
            'apartment': self.apartment,
            'full_address': self.get_full_address(),
            'blood_type': self.blood_type,
            'allergies': self.allergies,
            'medical_history': self.medical_history,
            'visit_datetime': self.visit_datetime.isoformat() if self.visit_datetime else None,
            'visit_type': self.visit_type,
            'hall_status': self.hall_status,
            'doctor_comments': self.doctor_comments,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'

