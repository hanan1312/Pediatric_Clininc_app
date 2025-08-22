# Pediatric Doctor Management System

A comprehensive desktop application designed specifically for pediatric healthcare professionals to manage patient records, generate reports, and streamline clinical workflows.

## Features

### ✨ Core Features
- **Patient Management**: Complete CRUD operations for patient records
- **Attractive UI**: Modern, responsive design with gradient themes and smooth animations
- **User-Friendly Interface**: Intuitive navigation with tabbed interface
- **Report Generation**: Professional PDF reports with patient information
- **Print Functionality**: Direct printing of patient reports
- **Search & Filter**: Quick patient search by name, ID, or parent information
- **Dashboard Analytics**: Overview statistics and key metrics

### 🏥 Patient Information Management
- Personal details (name, date of birth, gender)
- Parent/guardian information
- Contact details
- Medical history
- Known allergies
- Blood type
- Address information

### 📋 Report Features
- Professional PDF generation
- Comprehensive patient information
- Medical history and allergies
- Print-ready format
- Automatic report naming

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **PDF Generation**: ReportLab
- **Styling**: Custom CSS with modern design principles

## Installation Instructions

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)

### Step 1: Download and Extract
1. Download the application folder
2. Extract to your desired location (e.g., `C:\PediatricDoctorApp` or `/home/user/PediatricDoctorApp`)

### Step 2: Set Up Virtual Environment
```bash
# Navigate to the application directory
cd pediatric_doctor_app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
# Start the application
python src/main.py
```

### Step 5: Access the Application
1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. The application will be ready to use!

## Usage Guide

### Getting Started
1. **Dashboard**: View overview statistics and key metrics
2. **Add Patient**: Click the "Add Patient" tab to register new patients
3. **Patient Management**: View, search, and manage existing patients
4. **Reports**: Generate and print patient reports

### Adding a New Patient
1. Click on the "➕ Add Patient" tab
2. Fill in the required fields (marked with *)
3. Optionally add medical history, allergies, and other details
4. Click "Add Patient" to save

### Managing Patients
1. Go to the "👶 Patients" tab
2. Use the search box to find specific patients
3. Click "View Details" to see complete patient information
4. Generate reports directly from patient cards

### Generating Reports
1. **From Patient List**: Click "Generate Report" on any patient card
2. **From Reports Tab**: Select a patient from the dropdown and click "Generate & Print Report"
3. Reports are automatically downloaded and can be printed

### Printing Reports
- Reports are generated as PDF files
- Click the print button to send to your default printer
- Reports include all patient information and medical details

## Features Overview

### Dashboard
- Total patient count
- New patients this month
- Average patient age
- Reports generated

### Patient Management
- Add new patients with comprehensive information
- Search and filter existing patients
- View detailed patient profiles
- Edit patient information (future enhancement)

### Report Generation
- Professional PDF reports
- Complete patient information
- Medical history and allergies
- Print-ready format

## Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.11+ is installed
- Check that virtual environment is activated
- Verify all dependencies are installed

**Can't access the application:**
- Ensure the application is running (check terminal for "Running on...")
- Try accessing `http://127.0.0.1:5000` instead
- Check firewall settings

**Reports not generating:**
- Ensure ReportLab is properly installed
- Check browser's download settings
- Verify patient data is complete

### Support
For technical support or questions, please refer to the application logs in the terminal where you started the application.

## Security Notes

- This application is designed for local use
- Patient data is stored locally in SQLite database
- No data is transmitted over the internet
- Ensure proper backup of the database file (`src/database/app.db`)

## Data Backup

To backup patient data:
1. Copy the file `src/database/app.db`
2. Store in a secure location
3. To restore, replace the existing `app.db` file

## System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: Minimum 4GB, Recommended 8GB
- **Storage**: 500MB free space
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)

## License

This application is provided for educational and professional use in pediatric healthcare settings.

---

**Version**: 1.0.0  
**Last Updated**: July 2025  
**Developed for**: Pediatric Healthcare Professionals

