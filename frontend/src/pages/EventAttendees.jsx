import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';
import apiClient from '../services/apiClient';

const EventAttendees = () => {
    const { id } = useParams();
    const [attendees, setAttendees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [eventName, setEventName] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const eventResp = await api.get(`/api/event-manager/events/${id}`);
                setEventName(eventResp.data.event.nume);

                const ticketsResp = await api.get(`/api/event-manager/events/${id}/tickets`);
                const tickets = ticketsResp.data.tickets;

                const clientsData = await Promise.all(
                    tickets.map(async (t) => {
                        try {
                            const cod = t.bilet.cod;
                            // Apelam API-ul nou creat pe portul 8001
                            const clientResp = await apiClient.get(`/api/clients/ticket-owner/${cod}`);
                            return {
                                cod: cod,
                                nume: clientResp.data.nume,
                                email: clientResp.data.email
                            };
                        } catch (err) {
                            // Daca biletul e vandut dar inca neasignat unui cont de client
                            return { cod: t.bilet.cod, nume: 'Neasignat / Necunoscut', email: '-' };
                        }
                    })
                );

                setAttendees(clientsData);
            } catch (err) {
                console.error(err);
                alert("Nu s-au putut incarca datele participantilor.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [id]);

    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
            <h2>Participanți: {eventName}</h2>

            {loading ? <p>Se încarcă lista...</p> : (
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
                    <thead>
                        <tr style={{ backgroundColor: '#f2f2f2', textAlign: 'left' }}>
                            <th style={{ padding: '10px', border: '1px solid #ddd' }}>Cod Bilet</th>
                            <th style={{ padding: '10px', border: '1px solid #ddd' }}>Nume Client</th>
                            <th style={{ padding: '10px', border: '1px solid #ddd' }}>Email</th>
                        </tr>
                    </thead>
                    <tbody>
                        {attendees.length === 0 ? (
                            <tr><td colSpan="3" style={{padding: '10px', textAlign: 'center'}}>Niciun bilet vândut încă.</td></tr>
                        ) : (
                            attendees.map((person, index) => (
                                <tr key={index}>
                                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>{person.cod}</td>
                                    <td style={{ padding: '10px', border: '1px solid #ddd' }}><strong>{person.nume}</strong></td>
                                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>{person.email}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default EventAttendees;