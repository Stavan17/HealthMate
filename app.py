from flask_sqlalchemy import SQLAlchemy
import pdfkit
from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_mail import Mail, Message
import random
import string
from werkzeug.utils import secure_filename
import os
import plotly.express as px
import numpy as np
# from tensorflow.keras.preprocessing import image
# import tensorflow as tf
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import numpy as np,pandas as pd
import os
import csv
from dotenv import load_dotenv
# import pdfkit
from reportlab.pdfgen import canvas
from io import BytesIO
from flask.helpers import send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
mail = Mail(app)
load_dotenv()

app.secret_key = 'MYSECRETKEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT') or 465)
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail = Mail(app)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
  
    type_of_doctor = db.Column(db.String(50))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    type_of_doctor = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending')
    prescription_file = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))

def create_tables():
    with app.app_context():
        db.create_all()

def generate_random_string(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def send_mail(subject, recipient, body):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)
    
# Set the path to the directory containing text files
text_files_dir = os.path.join(os.path.dirname(__file__), 'static/prescriptions')

# Set the path to the directory where PDFs will be saved
pdf_output_dir = os.path.join(os.path.dirname(__file__), 'static/pdfs')

# Function to convert text file to PDF
def convert_to_pdf(file_path, output_path):
    with open(file_path, 'r') as file:
        content = file.read()

    pdfkit.from_string(content, output_path, {'title': 'PDF Conversion', 'footer-center': '[page]/[topage]'})
    
# ============================================================ model ============================================================ 


data = pd.read_csv(os.path.join("static","Data", "Training.csv"))
df = pd.DataFrame(data)
cols = df.columns
cols = cols[:-1]
x = df[cols]
y = df['prognosis']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)

dt = DecisionTreeClassifier()
clf_dt=dt.fit(x_train,y_train)

indices = [i for i in range(132)]
symptoms = df.columns.values[:-1]

dictionary = dict(zip(symptoms,indices))

def predict(symptom):
    user_input_symptoms = symptom
    user_input_label = [0 for i in range(132)]
    for i in user_input_symptoms:
        idx = dictionary[i]
        user_input_label[idx] = 1

    user_input_label = np.array(user_input_label)
    user_input_label = user_input_label.reshape((-1, 1)).transpose()

    # Get probabilities for all diseases
    probabilities = dt.predict_proba(user_input_label)[0]
    # Get indices of top 4 predictions sorted by probability
    top_4_indices = np.argsort(probabilities)[-4:][::-1]
    
    # Get the maximum probability for normalization
    max_prob = np.max(probabilities)
    
    predictions = []
    for idx in top_4_indices:
        disease = dt.classes_[idx]
        # Calculate relative confidence score
        confidence = (probabilities[idx] / max_prob) * 100
        predictions.append({
            'disease': disease,
            'confidence': round(float(confidence), 2)  # Round to 2 decimal places
        })
    
    return predictions

with open('static/Data/Testing.csv', newline='') as f:
        reader = csv.reader(f)
        symptoms = next(reader)
        symptoms = symptoms[:len(symptoms)-1]
        
# ============================================================ routes ============================================================ 

@app.route('/', methods=['GET', 'POST'])
def index():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        if user.type_of_doctor:
            appointments = Appointment.query.filter_by(type_of_doctor=user.type_of_doctor).all()
            return render_template('doctor-dashboard.html', username=username, appointments=appointments)
            
        else:
            user_appointments = user.appointments
            return render_template('patient-dashboard.html', username=username, user_appointments=user_appointments)
            
    return render_template('index.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        Email = user.email 
        user_appointments = user.appointments
        return render_template('patient-profile.html', username=username,Email=Email, user_appointments=user_appointments)
    return render_template('index')

@app.route('/patient-register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different username.', 'error')

    return render_template('patient-register.html')

@app.route('/doctor-register', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        type_of_doctor = request.form['type_of_doctor']
        user = User(username=username,email=email, password=password, type_of_doctor=type_of_doctor)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('index'))
    return render_template('doctor-register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Wrong username or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    username = None
    
    user = User.query.get(session['user_id'])
    username = user.username
    
    # Fetch distinct types of doctors from the database
    doctor_types = db.session.query(User.type_of_doctor).distinct().all()
    doctor_types = [doctor[0] for doctor in doctor_types]

    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        blood_group = request.form['blood_group']
        time_slot = request.form['time_slot']
        phone_number = request.form['phone_number']
        email = request.form['email']
        type_of_doctor = request.form['type_of_doctor']

        appointment = Appointment(
            name=name,
            age=age,
            blood_group=blood_group,
            time_slot=time_slot,
            phone_number=phone_number,
            email=email,
            type_of_doctor=type_of_doctor,
            user=user
        )

        db.session.add(appointment)
        db.session.commit()

        # Notify the doctor via email
        doctor_email = User.query.filter_by(type_of_doctor=type_of_doctor).first().email
        subject = 'New Appointment Request'
        body = f'Hello Doctor,\n\nYou have a new appointment request. Please log in to the system to approve or reject it.'
        send_mail(subject, doctor_email, body)

        return redirect(url_for('index'))

    return render_template('book-appointment.html',doctor_types=doctor_types,username=username)

@app.route('/approve-appointment/<int:appointment_id>')
def approve_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    doctor = User.query.get(session['user_id'])
    appointment = Appointment.query.get(appointment_id)

    if appointment.type_of_doctor != doctor.type_of_doctor:
        return redirect(url_for('index'))

    appointment.status = 'Approved'
    db.session.commit()

    # Notify the patient via email
    subject = 'Appointment Approved'
    body = f'Hello {appointment.name},\n\nYour appointment has been approved. Please log in to the system to view the details.'
    send_mail(subject, appointment.email, body)

    return redirect(url_for('index'))

@app.route('/policy')
def policy():
    return render_template('privacy-policy.html')

@app.route('/Transforming_Healthcare')
def Transforming_Healthcare():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('blog_Transforming Healthcare.html',username=username)
    return render_template('index.html')

@app.route('/Holistic_Health')
def Holistic_Health():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('blog_Holistic Health.html',username=username)
    return render_template('index.html')

@app.route('/Nourishing_Body')
def Nourishing_Body():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('blog_Nourishing_Body.html',username=username)
    return render_template('index.html')

@app.route('/Importance_of_Games')
def Importance_of_Games():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('blog_Importance_of_Games.html',username=username)
    return render_template('index.html')

@app.route('/admin')
def admin():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('admin.html',username=username)
    return render_template('index.html')

@app.route('/videocall')
def videocall():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('videocall.html',username=username)
    
    return render_template('index.html')

@app.route('/doctor-patients')
def doctor_patients():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username

        doctor = User.query.get(session['user_id'])

        if not doctor.type_of_doctor:
            return redirect(url_for('index'))

        # Fetch appointments assigned to the doctor
        appointments = Appointment.query.filter_by(type_of_doctor=doctor.type_of_doctor).all()
        file_list = os.listdir(text_files_dir)

        return render_template('doctor-patients.html', doctor=doctor, appointments=appointments,username=username,file_list=file_list)
    return render_template('index.html')

@app.route('/prescribe-medicine/<int:appointment_id>', methods=['GET', 'POST'])
def prescribe_medicine(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    doctor = User.query.get(session['user_id'])
    appointment = Appointment.query.get(appointment_id)

    if appointment.type_of_doctor != doctor.type_of_doctor:
        return redirect(url_for('index'))

    # available_medicines = ["Medicine 1", "Medicine 2", "Medicine 3"]  # Update this with your list of medicines
    available_medicines = [
    "Metformin: Diabetes",
    "Levothyroxine: Hypothyroidism",
    "Lisinopril: High Blood Pressure",
    "Atorvastatin: High Cholesterol",
    "Amlodipine: High Blood Pressure",
    "Omeprazole: Acid Reflux",
    "Metoprolol: High Blood Pressure",
    "Albuterol: Asthma",
    "Gabapentin: Nerve Pain",
    "Losartan: High Blood Pressure",
    "Fluticasone: Asthma",
    "Sertraline: Depression",
    "Hydrocodone/acetaminophen: Pain",
    "Montelukast: Asthma",
    "Bupropion: Depression",
    "Escitalopram: Depression",
    "Prednisone: Inflammation",
    "Ventolin HFA: Asthma",
    "Proair HFA: Asthma",
    "Advair Diskus: Asthma",
    "Latanoprost: Glaucoma",
    "Duloxetine: Depression",
    "Trazodone: Depression",
    "Azithromycin: Antibiotic",
    "Citalopram: Depression",
    "Amlodipine/atorvastatin: Blood Pressure/Cholesterol",
    "Warfarin: Blood Clots",
    "SPIRIVA: COPD",
    "Lyrica: Nerve Pain",
    "Advair HFA: Asthma",
    "Januvia: Diabetes",
    "Vyvanse: ADHD",
    "Nasonex: Allergies",
    "Pantoprazole: Acid Reflux",
    "Synthroid: Hypothyroidism",
    "Zoloft: Depression",
    "Celebrex: Arthritis",
    "Xanax: Anxiety",
    "Furosemide: Fluid Retention",
    "Prozac: Depression",
    "Simvastatin: High Cholesterol",
    "Spiriva Respimat: COPD",
    "Lexapro: Depression",
    "Lantus: Diabetes",
    "Viagra: Erectile Dysfunction",
    "Singulair: Asthma",
    "Crestor: High Cholesterol",
    "Amoxicillin: Antibiotic",
    "Cymbalta: Depression",
    "Flovent HFA: Asthma",
    "Victoza: Diabetes",
    "Tamsulosin: Enlarged Prostate",
    "Buspirone: Anxiety",
    "Allopurinol: Gout",
    "Lovastatin: High Cholesterol",
    "Ibuprofen: Pain/Inflammation",
    "Hydrochlorothiazide: High Blood Pressure",
    "Ventolin: Asthma",
    "Cephalexin: Antibiotic",
    "Meloxicam: Arthritis",
    "Clonazepam: Seizures/Anxiety",
    "Lipitor: High Cholesterol",
    "Nexium: Acid Reflux",
    "Premarin: Menopause",
    "Plavix: Blood Clots",
    "Dulera: Asthma",
    "Levemir: Diabetes",
    "Amitriptyline: Depression",
    "Humalog: Diabetes",
    "Invokana: Diabetes",
    "Symbicort: Asthma",
    "Glimepiride: Diabetes",
    "Flexeril: Muscle Spasms",
    "Novolog: Diabetes",
    "Bydureon: Diabetes",
    "Breo Ellipta: Asthma",
    "Janumet: Diabetes",
    "Strattera: ADHD",
    "NovoLog FlexPen: Diabetes",
    "Trulicity: Diabetes Type 2",
    "Benicar: High Blood Pressure",
    "Actos: Diabetes",
    "Pravastatin: High Cholesterol",
    "Farxiga: Diabetes",
    "Wellbutrin XL: Depression",
    "Jardiance: Diabetes",
    "Valacyclovir: Herpes",
    "Femara: Breast Cancer",
    "Ortho Tri-Cyclen: Birth Control",
    "Lamotrigine: Seizures",
    "Tramadol: Pain",
    "Flomax: Enlarged Prostate",
    "Prilosec OTC: Acid Reflux",
    "Bystolic: High Blood Pressure",
    "Aripiprazole: Schizophrenia",
    "Combivent Respimat: COPD",
    "Famotidine: Acid Reflux",
    "Liraglutide: Diabetes",
    "Carvedilol: High Blood Pressure",
    "Oxcarbazepine: Seizures"]


    if request.method == 'POST':
        selected_medicines = request.form.getlist('medicines[]')

        # Create a PDF document using ReportLab
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

        # Define styles for the header and footer
        styles = getSampleStyleSheet()
        header_style = ParagraphStyle(
            'Header1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            spaceAfter=12,
            textColor=colors.green,
        )

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
        )
        
        content = []

        # Add Jansevak header with green color and an <hr> tag
        jansevak_header = Paragraph("<font color='green' size='24'><b>Jansevak: We Care for Your Health</b></font><hr/>", header_style)
        content.append(jansevak_header)

        # Add space after Jansevak header
        content.append(Spacer(1, 12))

        # Add patient details with a larger font size
        patient_details = (
            f"<font size='14'><b>Patient Details:</b></font><br/>"
            f"<font size='12'>Name: {appointment.name}<br/>"
            f"Age: {appointment.age}<br/>"
            f"Blood Group: {appointment.blood_group}<br/>"
            f"Phone Number: {appointment.phone_number}</font>"
        )
        content.append(Paragraph(patient_details, styles['Normal']))

        # Add space after patient details
        content.append(Spacer(1, 12))

        # Add prescribed medicines with a larger font size
        prescribed_meds = "<font size='14'><b>Prescribed Medicines:</b></font><br/>"
        for medicine in selected_medicines:
            prescribed_meds += f"<font size='12'>- {medicine}<br/></font>"
        content.append(Paragraph(prescribed_meds, styles['Normal']))

        # Add space after prescribed medicines
        content.append(Spacer(1, 12))

        # Add doctor details and footer with a larger font size
        doctor_details = (
            f"<font size='14'><b>Prescribed by Dr. {doctor.username} ({doctor.type_of_doctor})</b></font><br/>"
            "<font size='12'>Thank you for choosing Jansevak! We wish you good health.</font>"
        )
        content.append(Paragraph(doctor_details, styles['Normal']))

        # Add space after doctor details
        content.append(Spacer(1, 12))

        # Add computer-generated e-prescription footer
        footer_text = (
            "<font size='12'><i>This is a computer-generated e-prescription and does not require any signature.</i></font>"
        )
        content.append(Paragraph(footer_text, styles['Normal']))

        # Build the PDF
        pdf.build(content)

        # Save the PDF to the file
        pdf_filename = f"prescription_{appointment_id}.pdf"
        pdf_filepath = os.path.join("static", "prescriptions", pdf_filename)
        buffer.seek(0)
        with open(pdf_filepath, 'wb') as pdf_file:
            pdf_file.write(buffer.read())

        buffer.close()

        # Update appointment status to 'Prescribed'
        appointment.status = 'Prescribed'
        appointment.prescription_file = pdf_filepath
        db.session.commit()
        
        # Notify the patient via email
        subject = 'Medicine Prescribed'
        body = f'Hello {appointment.name},\n\nYour medicines has been Prescribed by your dcotor. Please log in to the system to view the and downlaod the e-presciption.\n\nThank you for choosing Jansevak! We wish you good health.'
        send_mail(subject, appointment.email, body)

        return redirect(url_for('doctor_patients'))

    return render_template('prescribe-medicine.html', appointment=appointment, available_medicines=available_medicines)
    
@app.route('/view-prescription/<int:appointment_id>')
def view_prescription(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    doctor = User.query.get(session['user_id'])
    appointment = Appointment.query.get(appointment_id)

    if appointment.type_of_doctor != doctor.type_of_doctor or appointment.status != 'Prescribed':
        return redirect(url_for('index'))

    prescription_filepath = appointment.prescription_file

    return send_file(prescription_filepath, as_attachment=True)

@app.route('/view-prescription-patient/<int:appointment_id>')
def view_prescription_patient(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    appointment = Appointment.query.get(appointment_id)

    if not user or not appointment or appointment.user_id != user.id or appointment.status != 'Prescribed':
        return redirect(url_for('profile'))  # Change this line to redirect to the patient's profile instead of index

    # Read prescription text from the file
    prescription_filepath = appointment.prescription_file
    

    return send_file(prescription_filepath, as_attachment=True)

@app.route('/mentalhealth', methods=['GET', 'POST'])
def mentalhealth():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('mentalhealth.html',username=username)
    else:
        return render_template('index.html')

# ============================================================ scans ============================================================ 
    
@app.route('/braintumor', methods=['GET', 'POST'])
def braintumor():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('brain-tumor.html',username=username)
    else:
        return render_template('index.html')
    

@app.route('/disease_predict', methods=['POST'])
def disease_predict():
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        
        if not symptoms or len(symptoms) != 5:
            return jsonify({'error': 'Please provide exactly 5 symptoms'}), 400
            
        predictions = predict(symptoms)
        
        return jsonify({
            'predictions': predictions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/lung')
def lung():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('lung.html',username=username)
    else:
        return render_template('index.html')

@app.route('/cataract')
def cataract():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('cataract.html',username=username)
    return render_template('index.html')

@app.route('/get_symptoms')
def get_symptoms():
    try:
        # Get symptoms from the model's dictionary
        symptoms_list = list(dictionary.keys())
        return jsonify({'symptoms': symptoms_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)