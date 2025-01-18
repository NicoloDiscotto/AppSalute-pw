from flask import Flask, request, jsonify, session, send_from_directory
from datetime import datetime
import sqlite3
import os
import bcrypt

# Configurazione Flask
app = Flask(__name__, static_folder='../frontend/src')
app.config['PUBLIC_FOLDER'] = os.path.abspath('../frontend/public')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), '../db/app.db')
app.secret_key = os.urandom(24)

# Connessione al database
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Esegui una query generica
def execute_query(query, args=(), commit=False):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        if commit:
            conn.commit()
        return cursor.fetchall()

# Funzione generica per servire i file statici da directory specifiche
def serve_static_from_folder(folder, filename):
    return send_from_directory(os.path.join(app.static_folder, folder), filename)

# Route per login
@app.route('/')
def serve_login():
    return serve_static_from_folder('html', 'login.html')

# Route per index
@app.route('/index')
def serve_index_redirect():
    return serve_static_from_folder('html', 'index.html')

# Route per servire i file HTML
@app.route('/<page>.html')
def serve_html(page):
    return serve_static_from_folder('html', f'{page}.html')

# Route per servire i file CSS
@app.route('/<stylesheet>.css')
def serve_css(stylesheet):
    return serve_static_from_folder('css', f'{stylesheet}.css')

# Route per servire i file JS
@app.route('/<script>.js')
def serve_js(script):
    return serve_static_from_folder('js', f'{script}.js')

@app.route('/public/<path:filename>')
def serve_public(filename):
    return send_from_directory(app.config['PUBLIC_FOLDER'], filename)

# Verifica delle credenziali
def check_credentials(email, password):
    query = "SELECT password FROM users WHERE email = ?"
    result = execute_query(query, (email,))
    if result:
        stored_password = result[0]['password']
        return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
    return False

# Funzione per ottenere un utente per email
def get_user_by_email(email):
    query = "SELECT id, email FROM users WHERE email = ?"
    result = execute_query(query, (email,))
    return result[0] if result else None

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if check_credentials(email, password):
        user = get_user_by_email(email)
        session['user_id'] = user['id']
        return jsonify({"success": True, "message": "Login effettuato con successo!"})
    else:
        return jsonify({"success": False, "message": "Credenziali errate."}), 401
    
# Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"success": True, "message": "Logout effettuato con successo!"})

# Recupera la lista dei dottori
@app.route('/doctors', methods=['GET'])
def get_doctors():
    query = "SELECT * FROM doctors"
    doctors = execute_query(query)

    doctor_list = [{
            'id': doctor[0],
            'name': doctor[1],
            'specialization': doctor[2],
            'image_path': doctor[3]
        } for doctor in doctors]

    return jsonify(doctor_list)

# Prenotazione di una visita
@app.route('/book-appointment', methods=['POST'])
def book_appointment():
    data = request.json
    date = data.get('date')
    time_slot = data.get('timeSlot')
    doctor_id = data.get('doctorId')
    user_id = session.get('user_id')
        
    if not date or not time_slot or not doctor_id:
        return jsonify({"message": "Dati mancanti: assicurati di aver fornito data, fascia oraria e ID del medico."}), 400

    # Verifica se il medico esiste
    query = 'SELECT id FROM doctors WHERE id = ?'
    if not execute_query(query, (doctor_id,)):
        return jsonify({"message": "Il medico specificato non esiste."}), 404

    # Inserimento della prenotazione
    query = '''
        INSERT INTO bookings (user_id, doctor_id, date, time_slot)
        VALUES (?, ?, ?, ?)
    '''
    execute_query(query, (user_id, doctor_id, date, time_slot), commit=True)

    return jsonify({"message": "Prenotazione avvenuta con successo!"})

# Recupera le fasce orarie disponibili per un medico in una determinata data
@app.route('/available-time-slots', methods=['GET'])
def available_time_slots():
    doctor_id = request.args.get('doctorId')
    date = request.args.get('date')

    if not doctor_id or not date:
        return jsonify({"message": "Doctor ID o data mancanti"}), 400

    # Lista predefinita delle fasce orarie
    all_slots = [
        "09:00-10:00", "10:00-11:00", "11:00-12:00",
        "14:00-15:00", "15:00-16:00", "16:00-17:00"
    ]

    query = '''SELECT time_slot FROM bookings WHERE doctor_id = ? AND date = ?'''
    booked_slots = {slot[0] for slot in execute_query(query, (doctor_id, date))}
    available_slots = [slot for slot in all_slots if slot not in booked_slots]

    return jsonify({"availableSlots": available_slots})

# Recupero delle prenotazioni
@app.route('/my-bookings', methods=['GET'])
def my_bookings():
    user_id = session.get('user_id')
    query = '''
        SELECT bookings.id, doctors.name, bookings.date, bookings.time_slot
        FROM bookings
        JOIN doctors ON bookings.doctor_id = doctors.id
        WHERE bookings.user_id = ?
    '''
    bookings = execute_query(query, (user_id,))
    
    return jsonify([{
        "booking_id": booking[0], 
        "name": booking[1],
        "date": booking[2],
        "time_slot": booking[3]
    } for booking in bookings])

# Recupero di una prenotazione specifica
@app.route('/get-booking/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    query = ''' SELECT id, doctor_id, date, time_slot FROM bookings WHERE id = ? '''
    booking = execute_query(query, (booking_id,))

    if booking:
        booking = booking[0] 

        query = ''' 
            SELECT time_slot FROM bookings 
            WHERE doctor_id = ? AND date = ? AND id != ?
        '''
        booked_slots = execute_query(query, (booking['doctor_id'], booking['date'], booking_id))

        booked_slots = [slot['time_slot'] for slot in booked_slots]
        return jsonify({
            "date": booking['date'],
            "time_slot": booking['time_slot'],
            "booked_slots": booked_slots  
        })
    else:
        return jsonify({"message": "Prenotazione non trovata."}), 404

# Modifica di una prenotazione
@app.route('/update-booking/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    data = request.json
    date = data.get('date')
    time_slot = data.get('timeSlot')
    doctor_id = data.get('doctorId')

    if not date or not time_slot or not doctor_id:
        return jsonify({"message": "Dati mancanti."}), 400

    # Verifica se la nuova fascia oraria è già prenotata
    query = '''SELECT id FROM bookings WHERE doctor_id = (SELECT doctor_id FROM bookings WHERE id = ?) 
            AND date = ? AND time_slot = ? AND id != ?'''
    if execute_query(query, (booking_id, date, time_slot, booking_id)):
        return jsonify({"message": "Fascia oraria già prenotata."}), 400
        
    # Modifica della prenotazione
    query = '''UPDATE bookings SET date = ?, time_slot = ? WHERE id = ?'''
    execute_query(query, (date, time_slot, booking_id), commit=True)

    return jsonify({"message": "Prenotazione modificata con successo!"})

# Cancellazione di una prenotazione
@app.route('/delete-booking/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    query = 'SELECT id FROM bookings WHERE id = ?'
    booking = execute_query(query, (booking_id,))

    if not booking:
        return jsonify({"message": "Prenotazione non trovata."}), 404

    query = 'DELETE FROM bookings WHERE id = ?'
    execute_query(query, (booking_id,), commit=True)

    return jsonify({"message": "Prenotazione cancellata con successo!"})


# Gestione errori
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Risorsa non trovata"}), 404

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500


# Avvio dell'app
if __name__ == '__main__':
    app.run(debug=True)
