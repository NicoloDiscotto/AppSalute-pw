document.addEventListener('DOMContentLoaded', async () => {

    // Funzione per caricare i dottori dal server
    async function loadDoctors() {
        const doctorListElement = document.getElementById('doctorList');
        doctorListElement.innerHTML = '';

        try {
            // Effettua una richiesta al server per ottenere la lista dei dottori
            const response = await fetch('/doctors');
            if (!response.ok) {
                throw new Error(`Errore nel caricamento dei dottori: ${response.status} ${response.statusText}`);
            }

            const doctors = await response.json();

            // Se non ci sono dottori disponibili, mostra un messaggio
            if (doctors.length === 0) {
                showMessage('Nessun dottore disponibile al momento.');
                return;
            }

            // Crea e aggiungi un div per ogni dottore
            doctors.forEach(doctor => {
                const doctorDiv = createDoctorElement(doctor);
                doctorListElement.appendChild(doctorDiv);
            });

            // Aggiungi l'evento di click ai pulsanti "Prenota una visita"
            addBookingEventListeners();

        } catch (error) {
            showMessage('Errore durante il caricamento dei dottori. Riprova più tardi.');
            console.error(error);
        }
    }

    // Funzione per creare un elemento HTML per ogni dottore
    function createDoctorElement(doctor) {
        const doctorDiv = document.createElement('div');
        doctorDiv.classList.add('doctor');
        doctorDiv.innerHTML = `
            <h2>${doctor.specialization}</h2>
            <img src="${doctor.image_path}" alt="Immagine di ${doctor.name}" class="doctor-image">
            <p class="name">${doctor.name}</p>
            <button class="details-btn" data-doctor-id="${doctor.id}"> Prenota una visita</button>
        `;
        return doctorDiv;
    }

    // Funzione per aggiungere gli event listener ai pulsanti "Prenota una visita"
    function addBookingEventListeners() {
        document.querySelectorAll('.details-btn').forEach(button => {
            button.addEventListener('click', function () {
                const doctorId = this.getAttribute('data-doctor-id');
                if (doctorId) {
                    window.location.href = `/booking.html?doctorId=${doctorId}`;
                } else {
                    console.error('ID del dottore non valido.');
                }
            });
        });
    }

    // Funzione per mostrare messaggi all'utente
    function showMessage(message) {
        const doctorListElement = document.getElementById('doctorList');
        doctorListElement.innerHTML = `<p>${message}</p>`;
    }

    // Carica i dottori all'avvio della pagina
    await loadDoctors();

});