document.addEventListener('DOMContentLoaded', async () => {
    // Recupera i parametri dalla query string dell'URL
    const urlParams = new URLSearchParams(window.location.search);
    const doctorId = urlParams.get('doctorId');
    const bookingId = urlParams.get('bookingId');

    // Verifica la presenza dei parametri necessari
    if (!doctorId && !bookingId) {
        alert('Errore: ID del dottore o della prenotazione non trovati.');
        window.location.href = '/index';
        return;
    }

    // Se bookingId è presente, carica la prenotazione esistente
    if (bookingId) {
        await loadBookingDetails(bookingId);
    }

    // Carica le fasce orarie disponibili per la data selezionata
    document.getElementById('calendar').addEventListener('change', (e) => {
        loadTimeSlots(e.target.value);
    });

    // Gestione prenotazione
    document.getElementById('bookButton').addEventListener('click', async function () {
        await handleBooking(doctorId, bookingId);
    });

    // Funzione generica per gestire gli errori di connessione
    function handleConnectionError(error) {
        alert('Errore di connessione al server. Riprova più tardi.');
        console.error(error);
    }

    // Funzione per caricare i dettagli della prenotazione esistente
    async function loadBookingDetails(bookingId) {
        try {
            const response = await fetch(`/get-booking/${bookingId}`);
            const booking = await response.json();

            if (response.ok) {
                document.getElementById('calendar').value = booking.date;
                const selectedTimeSlot = document.querySelector(`input[value="${booking.time_slot}"]`);
                if (selectedTimeSlot) selectedTimeSlot.checked = true;
            } else {
                alert('Errore nel caricamento della prenotazione');
            }
        } catch (error) {
            handleConnectionError(error);
        }
    }

    // Funzione per caricare le fasce orarie disponibili
    async function loadTimeSlots(date) {
        if (!doctorId) {
            alert('Errore: ID del dottore non trovato.');
            return;
        }

        try {
            const response = await fetch(`/available-time-slots?doctorId=${doctorId}&date=${date}`);
            const data = await response.json();

            if (!response.ok) {
                alert('Errore nel recupero delle fasce orarie disponibili.');
                return;
            }

            updateTimeSlots(data.availableSlots);
        } catch (error) {
            handleConnectionError(error);
        }
    }

    // Funzione per aggiornare la lista delle fasce orarie
    function updateTimeSlots(slots) {
        const timeSlotsContainer = document.getElementById('time-slots');
        timeSlotsContainer.innerHTML = '';

        if (slots.length === 0) {
            timeSlotsContainer.innerHTML = '<p>Non ci sono fasce orarie disponibili per la data selezionata.</p>';
        } else {
            slots.forEach(slot => {
                const slotDiv = document.createElement('div');
                slotDiv.classList.add('time-slot');
                slotDiv.innerHTML = `
                    <input type="radio" name="timeSlot" value="${slot}" id="${slot}">
                    <label for="${slot}">${slot}</label>
                `;
                timeSlotsContainer.appendChild(slotDiv);
            });
        }
        document.getElementById('bookButton').disabled = false;
    }

    // Funzione per gestire la prenotazione
    async function handleBooking(doctorId, bookingId) {
        const date = document.getElementById('calendar').value;
        const timeSlot = document.querySelector('input[name="timeSlot"]:checked')?.value;

        if (!date || !timeSlot) {
            alert('Per favore, seleziona una data e una fascia oraria.');
            return;
        }

        // Verifica che la data selezionata non sia nel passato
        const italianTime = new Date(new Date().toLocaleString("en-US", { timeZone: "Europe/Rome" }));
        const [startTime] = timeSlot.split('-');
        const bookingDateTime = new Date(`${date}T${startTime}:00`);
        const localizedBookingDateTime = new Date(bookingDateTime.toLocaleString("en-US", { timeZone: "Europe/Rome" }));

        if (bookingDateTime < italianTime) {
            alert('Non puoi selezionare una data o un orario nel passato.');
            return;
        }

        // Disabilita il pulsante di prenotazione durante il caricamento
        const bookButton = document.getElementById('bookButton');
        bookButton.disabled = true;
        bookButton.innerText = 'Caricamento...';

        const endpoint = bookingId ? `/update-booking/${bookingId}` : '/book-appointment';
        const method = bookingId ? 'PUT' : 'POST';

        try {
            const body = { date, timeSlot, doctorId };
            const response = await fetch(endpoint, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });

            const result = await response.json();

            if (response.ok) {
                alert('Prenotazione avvenuta con successo!');
                window.location.href = '/index';
            } else {
                alert('Errore nella prenotazione: ' + result.message);
            }
        } catch (error) {
            handleConnectionError(error);
        } finally {
            bookButton.disabled = false;
            bookButton.innerText = 'Prenota';
        }
    }
});