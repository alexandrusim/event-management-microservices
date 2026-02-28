import { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import apiClient from '../services/apiClient';
import { AuthContext } from '../context/AuthContext';

const EventList = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [error, setError] = useState('');

    const ITEMS_PER_PAGE = 6;

    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const fetchEvents = async (pageNum) => {
        setLoading(true);
        try {
            const response = await api.get(`/api/event-manager/events?page=${pageNum}&items_per_page=${ITEMS_PER_PAGE}`);
            setEvents(response.data.events);
        } catch (err) {
            console.error(err);
            setError("Nu s-au putut incarca evenimentele.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEvents(page);
    }, [page]);

    const handleBuyTicket = async (eventId) => {
        if (!window.confirm("Confirmi achizitia unui bilet?")) return;
        try {
            const ticketResponse = await api.post(`/api/event-manager/events/${eventId}/tickets`);
            const ticketCode = ticketResponse.data.ticket.cod;

            try {
                await apiClient.post('/api/clients/me/tickets', { cod: ticketCode });
                alert(`Succes! Ai cumparat biletul ${ticketCode}`);
            } catch (mongoErr) {
                if (mongoErr.response && mongoErr.response.status === 404) {
                    await apiClient.post('/api/clients', {
                        prenume_nume: user.sub || "Client Nou",
                        email: user.email || "client@test.com",
                        telefon: "0700000000",
                        data_nasterii: "2000-01-01"
                    });
                    await apiClient.post('/api/clients/me/tickets', { cod: ticketCode });
                    alert(`Succes! Profil creat si biletul ${ticketCode} cumparat.`);
                } else {
                    throw mongoErr;
                }
            }
        } catch (err) {
            alert("Eroare la achizitie: " + (err.response?.data?.detail || err.message));
        }
    };

    const handleDelete = async (eventId) => {
        if(!window.confirm("Sigur stergi?")) return;
        try {
            await api.delete(`/api/event-manager/events/${eventId}`);
            fetchEvents(page);
        } catch(err) { alert("Eroare stergere"); }
    }

    const canManage = (eventOwnerId) => {
        if (!user) return false;
        if (user.role === 'admin') return true;
        const rawId = user.sub || user.user_id || user.id;
        return Number(rawId) === Number(eventOwnerId);
    };

    const styles = {
        container: {
            backgroundColor: '#121212',
            minHeight: '100vh',
            color: '#e0e0e0',
            fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif'
        },
        navbar: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '15px 40px',
            backgroundColor: '#1e1e1e',
            borderBottom: '1px solid #333',
            boxShadow: '0 2px 5px rgba(0,0,0,0.5)'
        },
        brand: {
            fontSize: '1.5rem',
            fontWeight: 'bold',
            color: '#ffffff'
        },
        userInfo: {
            display: 'flex',
            alignItems: 'center',
            gap: '20px'
        },
        navButton: {
            padding: '8px 16px',
            borderRadius: '4px',
            border: 'none',
            cursor: 'pointer',
            fontWeight: '600',
            transition: '0.2s'
        },
        gridContainer: {
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '25px',
            padding: '40px',
            maxWidth: '1200px',
            margin: '0 auto'
        },
        card: {
            backgroundColor: '#1e1e1e',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            border: '1px solid #333',
            transition: 'transform 0.2s',
        },
        cardTitle: {
            fontSize: '1.4rem',
            marginBottom: '10px',
            color: '#fff'
        },
        cardInfo: {
            color: '#b0b0b0',
            marginBottom: '5px',
            fontSize: '0.95rem'
        },
        buyButton: {
            marginTop: '15px',
            width: '100%',
            padding: '12px',
            backgroundColor: '#ffc107',
            color: '#000',
            border: 'none',
            borderRadius: '6px',
            fontWeight: 'bold',
            cursor: 'pointer',
            fontSize: '1rem'
        },
        pagination: {
            display: 'flex',
            justifyContent: 'center',
            gap: '15px',
            padding: '20px',
            alignItems: 'center'
        }
    };

    return (
        <div style={styles.container}>
            <nav style={styles.navbar}>
                <div style={styles.brand}>Event Manager</div>

                {user ? (
                    <div style={styles.userInfo}>
                        <span>Salut, <span style={{color: '#ffc107'}}>{user.sub || "User"}</span>!</span>

                        <button
                            onClick={() => navigate('/profile')}
                            style={{...styles.navButton, backgroundColor: '#333', color: 'white'}}
                        >
                            Profil
                        </button>

                        <button
                            onClick={() => { logout(); navigate('/login'); }}
                            style={{...styles.navButton, backgroundColor: '#dc3545', color: 'white'}}
                        >
                            Logout
                        </button>
                    </div>
                ) : (
                    <button
                        onClick={() => navigate('/login')}
                        style={{...styles.navButton, backgroundColor: '#007bff', color: 'white'}}
                    >
                        Login
                    </button>
                )}
            </nav>

            <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 40px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '30px' }}>
                    <h1>Evenimente Disponibile</h1>
                    {user && (user.role === 'owner-event' || user.role === 'admin') && (
                        <button
                            onClick={() => navigate('/events/new')}
                            style={{...styles.navButton, backgroundColor: '#28a745', color: 'white'}}
                        >
                            + Adaugă Eveniment
                        </button>
                    )}
                </div>

                {error && <p style={{ color: '#ff6b6b', textAlign: 'center' }}>{error}</p>}
            </div>

            {loading ? <p style={{textAlign: 'center', marginTop: '50px'}}>Se încarcă evenimentele...</p> : (
                <div style={styles.gridContainer}>
                    {events.map((item) => (
                        <div key={item.event.id} style={styles.card}>
                            <div>
                                <h3 style={styles.cardTitle}>{item.event.nume}</h3>
                                <p style={styles.cardInfo}>📍 <strong>Locație:</strong> {item.event.locatie}</p>
                                <p style={styles.cardInfo}>🎟️ <strong>Locuri:</strong> {item.event.numarLocuri}</p>
                                <p style={{...styles.cardInfo, fontStyle: 'italic', marginTop: '10px'}}>{item.event.descriere}</p>
                            </div>

                            {canManage(item.event.id_owner) && (
                                <div style={{ display: 'flex', gap: '5px', marginTop: '15px' }}>
                                    <button onClick={() => navigate(`/events/edit/${item.event.id}`)} style={{...styles.navButton, backgroundColor: '#007bff', color: 'white', flex: 1, fontSize: '0.8rem'}}>Edit</button>
                                    <button onClick={() => handleDelete(item.event.id)} style={{...styles.navButton, backgroundColor: '#dc3545', color: 'white', flex: 1, fontSize: '0.8rem'}}>Șterge</button>
                                    <button onClick={() => navigate(`/events/${item.event.id}/attendees`)} style={{...styles.navButton, backgroundColor: '#17a2b8', color: 'white', flex: 1, fontSize: '0.8rem'}}>Clienți</button>
                                </div>
                            )}

                            {user && user.role === 'client' && (
                                <button
                                    onClick={() => handleBuyTicket(item.event.id)}
                                    style={styles.buyButton}
                                >
                                    Cumpără Bilet
                                </button>
                            )}
                        </div>
                    ))}
                </div>
            )}

            <div style={styles.pagination}>
                <button
                    disabled={page === 1}
                    onClick={() => setPage(p => p - 1)}
                    style={{...styles.navButton, backgroundColor: '#333', color: 'white', opacity: page===1 ? 0.5 : 1}}
                >
                    &laquo; Înapoi
                </button>
                <span>Pagina {page}</span>
                <button
                    disabled={events.length < ITEMS_PER_PAGE}
                    onClick={() => setPage(p => p + 1)}
                    style={{...styles.navButton, backgroundColor: '#333', color: 'white', opacity: events.length < ITEMS_PER_PAGE ? 0.5 : 1}}
                >
                    Înainte &raquo;
                </button>
            </div>
        </div>
    );
};

export default EventList;