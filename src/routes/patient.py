from flask import Blueprint, request, jsonify
from datetime import datetime, date
import json # Import json module for handling JSON strings

from src.models.patient import Patient
from src.models.user import db

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/patients', methods=['GET'])
def get_all_patients():
    """Get all patients"""
    try:
        patients = Patient.query.order_by(Patient.created_at.desc()).all()
        return jsonify([patient.to_dict() for patient in patients]), 200
    except Exception as e:
        print(f"Error in get_all_patients: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a specific patient by ID"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        print(f"Error in get_patient: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'parent_name', 'phone']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse date of birth
        try:
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. UseYYYY-MM-DD'}), 400
        
        # Handle allergies: convert list to JSON string if provided as a list
        allergies_data = data.get('allergies')
        if isinstance(allergies_data, list):
            allergies_str = json.dumps(allergies_data)
        elif isinstance(allergies_data, str):
            allergies_str = allergies_data.strip()
        else:
            allergies_str = None # Or an empty string if preferred

        # Handle medical_history: ensure it's a string
        medical_history_data = data.get('medical_history')
        if isinstance(medical_history_data, str):
            medical_history_str = medical_history_data.strip()
        else:
            medical_history_str = None # Or an empty string if preferred
        
        # Create new patient with new address fields
        patient = Patient(
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            date_of_birth=date_of_birth,
            gender=data['gender'],
            parent_name=data['parent_name'].strip(),
            phone=data['phone'].strip(),
            patient_phone=data.get('patient_phone', '').strip() if data.get('patient_phone') else None,
            city=data.get('city', '').strip(),
            area=data.get('area', '').strip(),
            street=data.get('street', '').strip(),
            apartment=data.get('apartment', '').strip(),
            blood_type=data.get('blood_type', '').strip(),
            allergies=allergies_str, # Use the processed string
            medical_history=medical_history_str, # Use the processed string
            # visit_datetime and visit_type are now explicitly excluded from initial patient creation
            visit_datetime=None,
            visit_type=None, # This line explicitly sets it to None
            hall_status='Out', # Default status
            doctor_comments=None,
            status='registered' # Default status for new patient
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify(patient.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_patient: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update an existing patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'first_name' in data:
            patient.first_name = data['first_name'].strip()
        if 'last_name' in data:
            patient.last_name = data['last_name'].strip()
        if 'date_of_birth' in data:
            try:
                patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. UseYYYY-MM-DD'}), 400
        if 'gender' in data:
            patient.gender = data['gender']
        if 'parent_name' in data:
            patient.parent_name = data['parent_name'].strip()
        if 'phone' in data:
            patient.phone = data['phone'].strip()
        if 'patient_phone' in data:
            patient.patient_phone = data['patient_phone'].strip() if data['patient_phone'] else None
        
        # Update new address fields
        if 'city' in data:
            patient.city = data['city'].strip()
        if 'area' in data:
            patient.area = data['area'].strip()
        if 'street' in data:
            patient.street = data['street'].strip()
        if 'apartment' in data:
            patient.apartment = data['apartment'].strip()

        if 'blood_type' in data:
            patient.blood_type = data['blood_type'].strip()
        
        # Handle allergies for update
        if 'allergies' in data:
            allergies_data = data.get('allergies')
            if isinstance(allergies_data, list):
                patient.allergies = json.dumps(allergies_data)
            elif isinstance(allergies_data, str):
                patient.allergies = allergies_data.strip()
            else:
                patient.allergies = None # Or an empty string if preferred

        # Handle medical_history for update
        if 'medical_history' in data:
            medical_history_data = data.get('medical_history')
            if isinstance(medical_history_data, str):
                patient.medical_history = medical_history_data.strip()
            else:
                patient.medical_history = None # Or an empty string if preferred
        
        # visit_type is removed from update_patient to ensure it's only set via reservation
        # if 'visit_type' in data:
        #     patient.visit_type = data['visit_type']
        
        visit_datetime_str = data.get('visit_datetime')
        if visit_datetime_str: # Check if it's not None or empty string
            try:
                # Replace 'Z' with '+00:00' for full ISO 8601 compatibility with fromisoformat
                if visit_datetime_str.endswith('Z'):
                    visit_datetime_str = visit_datetime_str[:-1] + '+00:00'
                patient.visit_datetime = datetime.fromisoformat(visit_datetime_str)
            except ValueError:
                print(f"DEBUG: Failed to parse visit_datetime in update_patient: '{visit_datetime_str}'")
                return jsonify({'error': 'Invalid visit_datetime format. Use ISO 8601 string.'}), 400
        else:
            patient.visit_datetime = None # Explicitly set to None if not provided or empty

        if 'hall_status' in data:
            patient.hall_status = data['hall_status']
        if 'doctor_comments' in data:
            patient.doctor_comments = data['doctor_comments']
        if 'status' in data:
            patient.status = data['status']

        patient.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(patient.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_patient: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete a patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        db.session.delete(patient)
        db.session.commit()
        
        return jsonify({'message': 'Patient deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_patient: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/search', methods=['GET'])
def search_patients():
    """Search patients by name or parent name"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify([]), 200
        
        patients = Patient.query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{query}%'),
                Patient.last_name.ilike(f'%{query}%'),
                Patient.parent_name.ilike(f'%{query}%')
            )
        ).order_by(Patient.created_at.desc()).all()
        
        return jsonify([patient.to_dict() for patient in patients]), 200
        
    except Exception as e:
        print(f"Error in search_patients: {e}")
        return jsonify({'error': str(e)}), 500

from flask import send_file
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import os

@patient_bp.route('/patients/<int:patient_id>/report', methods=['POST'])
def generate_patient_report(patient_id):
    """Generate a PDF report for a specific patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        story = []
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#4a5568')
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#667eea')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6
        )
        
        today = date.today()
        age = today.year - patient.date_of_birth.year - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))
        
        story.append(Paragraph("🏥 PEDIATRIC PATIENT REPORT", title_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Patient Information", header_style))
        
        patient_data = [
            ['Patient ID:', str(patient.id)],
            ['Full Name:', f"{patient.first_name} {patient.last_name}"],
            ['Date of Birth:', patient.date_of_birth.strftime('%B %d, %Y')],
            ['Age:', f"{age} years old"],
            ['Gender:', patient.gender],
            ['Parent/Guardian:', patient.parent_name],
            ['Phone Number:', patient.phone],
        ]
        
        address_parts = []
        if patient.apartment:
            address_parts.append(f"Apartment {patient.apartment}")
        if patient.street:
            address_parts.append(patient.street)
        if patient.area:
            address_parts.append(patient.area)
        if patient.city:
            address_parts.append(patient.city)
            
        full_address = ", ".join(filter(None, address_parts))
        if full_address:
            patient_data.append(['Address:', full_address])
        
        if patient.visit_type:
            patient_data.append(['Visit Type:', patient.visit_type.title()])
        
        if patient.visit_datetime:
            patient_data.append(['Visit Date/Time:', patient.visit_datetime.strftime('%B %d, %Y at %I:%M %p')])
        
        if patient.blood_type:
            patient_data.append(['Blood Type:', patient.blood_type])
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a5568')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        if patient.allergies:
            try:
                # Attempt to load as JSON, if it fails, treat as plain text
                allergies_list = json.loads(patient.allergies)
                if allergies_list:
                    story.append(Paragraph("Known Allergies", header_style))
                    allergies_text = ", ".join(allergies_list)
                    story.append(Paragraph(f"⚠️ {allergies_text}", normal_style))
                    story.append(Spacer(1, 15))
            except (json.JSONDecodeError, TypeError):
                if patient.allergies.strip():
                    story.append(Paragraph("Known Allergies", header_style))
                    story.append(Paragraph(f"⚠️ {patient.allergies}", normal_style))
                    story.append(Spacer(1, 15))
        
        if patient.medical_history:
            story.append(Paragraph("Medical History", header_style))
            story.append(Paragraph(patient.medical_history, normal_style))
            story.append(Spacer(1, 15))
        
        if patient.doctor_comments:
            story.append(Paragraph("Doctor's Comments", header_style))
            story.append(Paragraph(patient.doctor_comments, normal_style))
            story.append(Spacer(1, 15))
        
        if hasattr(patient, 'status') and patient.status:
            story.append(Paragraph("Visit Status", header_style))
            status_text = patient.status.replace('_', ' ').title()
            if hasattr(patient, 'hall_status') and patient.hall_status:
                status_text += f" (Hall Status: {patient.hall_status})"
            story.append(Paragraph(status_text, normal_style))
            story.append(Spacer(1, 15))
        
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#718096')
        )
        
        story.append(Paragraph("Generated by Pediatric Doctor Management System", footer_style))
        story.append(Paragraph(f"Report generated on: {date.today().strftime('%B %d, %Y')}", footer_style))
        
        doc.build(story)
        
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'patient_{patient.id}_report.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Error in generate_patient_report: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/<int:patient_id>/reservation', methods=['POST'])
def create_reservation(patient_id):
    """Create a new reservation for an existing patient"""
    try:
        data = request.get_json()
        patient = Patient.query.get_or_404(patient_id)
        
        # visit_type is now handled ONLY here for reservations
        patient.visit_type = data.get('visit_type')
        
        visit_datetime_str = data.get('visit_datetime')
        if visit_datetime_str: # Check if it's not None or empty string
            try:
                # Replace 'Z' with '+00:00' for full ISO 8601 compatibility
                if visit_datetime_str.endswith('Z'):
                    visit_datetime_str = visit_datetime_str[:-1] + '+00:00'
                patient.visit_datetime = datetime.fromisoformat(visit_datetime_str)
            except ValueError:
                print(f"DEBUG: Failed to parse visit_datetime in create_reservation: '{visit_datetime_str}'")
                return jsonify({'error': 'Invalid visit_datetime format. Use ISO 8601 string.'}), 400
        else:
            patient.visit_datetime = None # Explicitly set to None if not provided or empty

        patient.hall_status = data.get('hall_status', 'Out')
        patient.status = data.get('status', 'scheduled')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reservation created successfully',
            'patient_id': patient.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_reservation: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/<int:patient_id>/hall-status', methods=['POST'])
def update_hall_status(patient_id):
    """Update patient hall status and overall status"""
    try:
        data = request.get_json()
        patient = Patient.query.get_or_404(patient_id)
        
        patient.hall_status = data.get('hall_status', 'Out')
        patient.status = data.get('status', 'waiting')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Hall status updated successfully',
            'patient_id': patient.id,
            'hall_status': patient.hall_status,
            'status': patient.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_hall_status: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/<int:patient_id>/comments', methods=['POST'])
def save_doctor_comments(patient_id):
    """Save doctor's comments for a patient"""
    try:
        data = request.get_json()
        patient = Patient.query.get_or_404(patient_id)
        
        patient.doctor_comments = data.get('comments', '')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Comments saved successfully',
            'patient_id': patient.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in save_doctor_comments: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get comprehensive statistics for dashboard"""
    try:
        from datetime import datetime, timedelta
        
        now = datetime.now()
        today = now.date()
        current_month = now.month
        current_year = now.year
        
        total_patients = Patient.query.count()
        
        start_of_month = datetime(current_year, current_month, 1)
        new_this_month = Patient.query.filter(
            Patient.created_at >= start_of_month
        ).count()
        
        today_patients = Patient.query.filter(
            db.func.date(Patient.visit_datetime) == today
        ).count()
        
        patients = Patient.query.all()
        if patients:
            total_age = sum(
                (now.date() - patient.date_of_birth).days // 365 
                for patient in patients
            )
            avg_age = total_age // len(patients)
        else:
            avg_age = 0
        
        examination_count = Patient.query.filter_by(visit_type='examination').count()
        fast_examination_count = Patient.query.filter_by(visit_type='fast examination').count()
        consultation_count = Patient.query.filter_by(visit_type='consultation').count()
        
        in_hall_count = Patient.query.filter_by(hall_status='In').count()
        finished_count = Patient.query.filter_by(status='finished').count()
        
        return jsonify({
            'total_patients': total_patients,
            'new_this_month': new_this_month,
            'today_patients': today_patients,
            'average_age': avg_age,
            'visit_types': {
                'examination': examination_count,
                'fast_examination': fast_examination_count,
                'consultation': consultation_count
            },
            'hall_status': {
                'in_hall': in_hall_count,
                'finished': finished_count
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_statistics: {e}")
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/patients/daily-reset', methods=['POST'])
def daily_reset():
    """Reset daily patient status and clear reservations"""
    try:
        # Reset all patients to 'Out' hall status and clear visit information for new day
        patients = Patient.query.all()
        for patient in patients:
            if patient.status in ['in_hall', 'finished']:
                patient.hall_status = 'Out'
                patient.status = 'registered'
                patient.visit_datetime = None
                patient.visit_type = None
                patient.doctor_comments = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Daily reset completed successfully',
            'reset_count': len(patients)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in daily_reset: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/search-history/<patient_name>', methods=['GET'])
def search_patient_history(patient_name):
    """Search for patient by name and get complete visit history"""
    try:
        # Search for patients by name (first name or last name)
        patients = Patient.query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{patient_name}%'),
                Patient.last_name.ilike(f'%{patient_name}%')
            )
        ).order_by(Patient.created_at.desc()).all()
        
        if not patients:
            return jsonify({'message': 'No patients found with that name'}), 404
        
        # Get complete history for each patient
        patient_histories = []
        for patient in patients:
            # For now, we'll return the patient data with all visit information
            # In a more complex system, you might have a separate visits table
            history = {
                'patient_info': patient.to_dict(),
                'visit_history': [
                    {
                        'visit_date': patient.visit_datetime.isoformat() if patient.visit_datetime else None,
                        'visit_type': patient.visit_type,
                        'doctor_comments': patient.doctor_comments,
                        'status': patient.status,
                        'hall_status': patient.hall_status
                    }
                ] if patient.visit_datetime else []
            }
            patient_histories.append(history)
        
        return jsonify({
            'patients_found': len(patients),
            'patient_histories': patient_histories
        }), 200
        
    except Exception as e:
        print(f"Error in search_patient_history: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/<int:patient_id>/history-report', methods=['POST'])
def generate_patient_history_report(patient_id):
    """Generate a comprehensive history report for a specific patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        story = []
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#4a5568')
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#667eea')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6
        )
        
        today = date.today()
        age = today.year - patient.date_of_birth.year - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))
        
        story.append(Paragraph("🏥 PATIENT HISTORY REPORT", title_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Patient Information", header_style))
        
        patient_data = [
            ['Patient ID:', str(patient.id)],
            ['Full Name:', f"{patient.first_name} {patient.last_name}"],
            ['Date of Birth:', patient.date_of_birth.strftime('%B %d, %Y')],
            ['Age:', f"{age} years old"],
            ['Gender:', patient.gender],
            ['Parent/Guardian:', patient.parent_name],
            ['Parent Phone:', patient.phone],
        ]
        
        if patient.patient_phone:
            patient_data.append(['Patient Phone:', patient.patient_phone])
        
        address_parts = []
        if patient.apartment:
            address_parts.append(f"Apartment {patient.apartment}")
        if patient.street:
            address_parts.append(patient.street)
        if patient.area:
            address_parts.append(patient.area)
        if patient.city:
            address_parts.append(patient.city)
            
        full_address = ", ".join(filter(None, address_parts))
        if full_address:
            patient_data.append(['Address:', full_address])
        
        if patient.blood_type:
            patient_data.append(['Blood Type:', patient.blood_type])
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a5568')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        # Visit History Section
        story.append(Paragraph("Visit History", header_style))
        
        if patient.visit_datetime:
            visit_data = [
                ['Visit Date/Time:', patient.visit_datetime.strftime('%B %d, %Y at %I:%M %p')],
                ['Visit Type:', patient.visit_type.title() if patient.visit_type else 'Not specified'],
                ['Status:', patient.status.replace('_', ' ').title() if patient.status else 'Not specified'],
                ['Hall Status:', patient.hall_status if patient.hall_status else 'Not specified']
            ]
            
            visit_table = Table(visit_data, colWidths=[2*inch, 4*inch])
            visit_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f8ff')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a5568')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))
            
            story.append(visit_table)
            story.append(Spacer(1, 15))
        else:
            story.append(Paragraph("No visit history recorded.", normal_style))
            story.append(Spacer(1, 15))
        
        if patient.allergies:
            try:
                # Attempt to load as JSON, if it fails, treat as plain text
                allergies_list = json.loads(patient.allergies)
                if allergies_list:
                    story.append(Paragraph("Known Allergies", header_style))
                    allergies_text = ", ".join(allergies_list)
                    story.append(Paragraph(f"⚠️ {allergies_text}", normal_style))
                    story.append(Spacer(1, 15))
            except (json.JSONDecodeError, TypeError):
                if patient.allergies.strip():
                    story.append(Paragraph("Known Allergies", header_style))
                    story.append(Paragraph(f"⚠️ {patient.allergies}", normal_style))
                    story.append(Spacer(1, 15))
        
        if patient.medical_history:
            story.append(Paragraph("Medical History", header_style))
            story.append(Paragraph(patient.medical_history, normal_style))
            story.append(Spacer(1, 15))
        
        if patient.doctor_comments:
            story.append(Paragraph("Doctor's Comments & Medications", header_style))
            story.append(Paragraph(patient.doctor_comments, normal_style))
            story.append(Spacer(1, 15))
        
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#718096')
        )
        
        # Add doctor's name and clinic phone to footer
        story.append(Paragraph("Dr. [Doctor Name] - [Clinic Name]", footer_style))
        story.append(Paragraph("Clinic Phone: [Clinic Phone Number]", footer_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Generated by Pediatric Doctor Management System", footer_style))
        story.append(Paragraph(f"Report generated on: {date.today().strftime('%B %d, %Y')}", footer_style))
        
        doc.build(story)
        
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'patient_{patient.id}_history_report.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Error in generate_patient_history_report: {e}")
        return jsonify({'error': str(e)}), 500



@patient_bp.route('/patients/submit-to-hall', methods=['POST'])
def submit_to_hall():
    """Submit only 'In' patients from today's reservations to awaiting hall"""
    try:
        from datetime import datetime, date
        
        today = date.today()
        
        # Find today's patients with 'In' hall_status who are not already in hall or finished
        today_in_patients = Patient.query.filter(
            db.func.date(Patient.visit_datetime) == today,
            Patient.hall_status == 'In',
            Patient.status.notin_(['in_hall', 'finished'])  # Not already in hall or finished
        ).all()
        
        if not today_in_patients:
            return jsonify({'message': 'No "In" patients to submit to hall'}), 200
        
        # Update status to 'in_hall' for these patients
        for patient in today_in_patients:
            patient.status = 'in_hall'
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(today_in_patients)} "In" patients submitted to awaiting hall successfully',
            'submitted_count': len(today_in_patients)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in submit_to_hall: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/return-to-today', methods=['POST'])
def return_to_today():
    """Return patients from awaiting hall back to today's patients if not finished"""
    try:
        data = request.get_json()
        patient_ids = data.get('patient_ids', [])
        
        if not patient_ids:
            return jsonify({'error': 'No patient IDs provided'}), 400
        
        # Find patients in awaiting hall
        patients_to_return = Patient.query.filter(
            Patient.id.in_(patient_ids),
            Patient.status == 'in_hall'
        ).all()
        
        if not patients_to_return:
            return jsonify({'message': 'No patients found in awaiting hall'}), 200
        
        # Return them to today's patients (status: scheduled)
        for patient in patients_to_return:
            patient.status = 'scheduled'
            # Keep their original hall_status (In or Out)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(patients_to_return)} patients returned to today\'s patients',
            'returned_count': len(patients_to_return)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in return_to_today: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/finish-selected', methods=['POST'])
def finish_selected_patients():
    """Finish selected patients from awaiting hall"""
    try:
        data = request.get_json()
        patient_ids = data.get('patient_ids', [])
        
        if not patient_ids:
            return jsonify({'error': 'No patient IDs provided'}), 400
        
        # Find patients in awaiting hall
        patients_to_finish = Patient.query.filter(
            Patient.id.in_(patient_ids),
            Patient.status == 'in_hall'
        ).all()
        
        if not patients_to_finish:
            return jsonify({'message': 'No patients found in awaiting hall'}), 200
        
        # Mark them as finished
        for patient in patients_to_finish:
            patient.status = 'finished'
            patient.hall_status = 'Out'  # They leave the hall when finished
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(patients_to_finish)} patients marked as finished',
            'finished_count': len(patients_to_finish)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in finish_selected_patients: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/today', methods=['GET'])
def get_today_patients():
    """Get today's patients with their current status"""
    try:
        from datetime import date
        
        today = date.today()
        
        today_patients = Patient.query.filter(
            db.func.date(Patient.visit_datetime) == today
        ).order_by(Patient.visit_datetime).all()
        
        return jsonify([patient.to_dict() for patient in today_patients]), 200
        
    except Exception as e:
        print(f"Error in get_today_patients: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/awaiting', methods=['GET'])
def get_awaiting_patients():
    """Get patients currently in awaiting hall"""
    try:
        awaiting_patients = Patient.query.filter(
            Patient.status == 'in_hall'
        ).order_by(Patient.visit_datetime).all()
        
        return jsonify([patient.to_dict() for patient in awaiting_patients]), 200
        
    except Exception as e:
        print(f"Error in get_awaiting_patients: {e}")
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/patients/finished', methods=['GET'])
def get_finished_patients():
    """Get patients who have finished their visits"""
    try:
        finished_patients = Patient.query.filter(
            Patient.status == 'finished'
        ).order_by(Patient.visit_datetime.desc()).all()
        
        return jsonify([patient.to_dict() for patient in finished_patients]), 200
        
    except Exception as e:
        print(f"Error in get_finished_patients: {e}")
        return jsonify({'error': str(e)}), 500

