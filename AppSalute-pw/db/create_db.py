import sqlite3
import bcrypt


def create_database():
    try:
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()

        # Creazione della tabella 'users'
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
            )
        ''')

        # Genera hash delle password
        password1 = bcrypt.hashpw('12345678'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        password2 = bcrypt.hashpw('12345678'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Inserimento degli utenti
        cursor.execute('''
        INSERT OR IGNORE INTO users (email, password) VALUES 
        ('mario.rossi@example.com', ?),
        ('mattia.gialli@example.com', ?)
        ''',(password1, password2))

        # Creazione della tabella 'doctors'
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            image_path TEXT NOT NULL
            )
        ''')

        # Inserimento dei dottori
        cursor.execute('''
        INSERT OR IGNORE INTO doctors (name, specialization, image_path) VALUES
        ('Dott.ssa Aurora Neri', 'Dermatologa', '/public/icons-doc-3.png'),
        ('Dott. Marco Verdi', 'Oculista', '/public/icons-doc-1.png'),
        ('Dott. Luca Bianchi', 'Fisioterapista', '/public/icons-doc-2.png'),
        ('Dott.ssa Giulia Viola', 'Nutrizionista', '/public/icons-doc-4.png')
        ''')
    
        # Creazione della tabella 'bookings'
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
        ''')
        conn.commit()
        print("Database creato e popolato con successo!")

    except sqlite3.Error as e:
        print(f"Errore: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_database()