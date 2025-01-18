document.addEventListener('DOMContentLoaded', function () {

    // Funzione per gestire il logout
    async function handleLogout() {
        const isConfirmed = confirm('Sei sicuro di voler uscire?');

        if (isConfirmed) {
            try {
                // Invia richiesta di logout al server
                const response = await fetch('/logout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                // Gestisci la risposta del server
                const result = await response.json();

                if (response.ok) {
                    window.location.href = '/';
                } else {
                    alert('Errore durante il logout: ' + result.message);
                }
            } catch (error) {
                handleNetworkError(error);
            }
        }
    };

    // Funzione di gestione errore di rete
    function handleNetworkError(error) {
        alert('Errore di rete. Riprova più tardi.');
        console.error(error);
    }

    // Funzione di reindirizzamento
    function redirectTo(url) {
        window.location.href = url;
    }

    // Aggiungi l'event listener per il pulsante di logout
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
    }

    // Aggiungi l'event listener per il pulsante "Le Mie Prenotazioni"
    const myBookingsButton = document.getElementById('myBookingsButton');
    if (myBookingsButton) {
        myBookingsButton.addEventListener('click', function () {
            redirectTo('/mybooking.html');
        });
    }
});