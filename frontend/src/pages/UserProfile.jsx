import { useEffect, useState, useContext } from 'react';
import apiClient from '../services/apiClient';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const UserProfile = () => {
    const { user } = useContext(AuthContext);
    const navigate = useNavigate();

    const [profile, setProfile] = useState({
        prenume_nume: '',
        email: '',
        telefon: '',
        data_nasterii: ''
    });
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const profileResp = await apiClient.get('/api/clients/me');
                setProfile(profileResp.data);

                const ticketsResp = await apiClient.get('/api/clients/me/tickets');
                setTickets(ticketsResp.data.tickets);
            } catch (err) {
                if(err.response?.status === 404) {
                    setProfile(p => ({...p, email: user.email || ""}));
                }
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [user]);

    const handleSaveProfile = async (e) => {
        e.preventDefault();
        setMessage('');
        try {
            try {
                 await apiClient.put('/api/clients/me', profile);
                 setMessage(" Profil actualizat cu succes!");
            } catch (putErr) {
                if (putErr.response?.status === 404) {
                    await apiClient.post('/api/clients', {
                        ...profile,
                        prenume_nume: profile.prenume_nume || user.sub,
                        email: profile.email || user.email || "client@test.com"
                    });
                    setMessage(" Profil creat cu succes!");
                } else {
                    throw putErr;
                }
            }
        } catch (err) {
            console.error(err);
            setMessage(" Eroare la salvarea profilului.");
        }
    };

    const styles = {
        container: {
            backgroundColor: '#121212',
            minHeight: '100vh',
            color: '#e0e0e0',
            fontFamily: 'Segoe UI, sans-serif',
            padding: '40px 20px'
        },
        header: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            maxWidth: '1000px',
            margin: '0 auto 40px auto',
            borderBottom: '1px solid #333',
            paddingBottom: '20px'
        },
        backButton: {
            padding: '10px 20px',
            backgroundColor: '#333',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.9rem',
            transition: '0.2s'
        },
        contentGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '40px',
            maxWidth: '1000px',
            margin: '0 auto'
        },
        card: {
            backgroundColor: '#1e1e1e',
            padding: '30px',
            borderRadius: '12px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
            border: '1px solid #333'
        },
        sectionTitle: {
            borderBottom: '1px solid #444',
            paddingBottom: '10px',
            marginBottom: '20px',
            color: '#ffc107',
            fontSize: '1.4rem'
        },
        formGroup: {
            marginBottom: '15px'
        },
        label: {
            display: 'block',
            marginBottom: '8px',
            color: '#aaa',
            fontSize: '0.9rem'
        },
        input: {
            width: '100%',
            padding: '12px',
            borderRadius: '6px',
            border: '1px solid #444',
            backgroundColor: '#2c2c2c',
            color: 'white',
            fontSize: '1rem',
            outline: 'none'
        },
        saveButton: {
            width: '100%',
            padding: '12px',
            marginTop: '10px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold'
        },
        ticketCard: {
            backgroundColor: '#2c2c2c',
            borderLeft: '5px solid #28a745',
            padding: '15px',
            marginBottom: '15px',
            borderRadius: '4px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
        },
        ticketCode: {
            fontSize: '1.1rem',
            fontWeight: 'bold',
            color: '#fff',
            fontFamily: 'monospace'
        },
        badge: {
            backgroundColor: 'rgba(40, 167, 69, 0.2)',
            color: '#28a745',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 'bold'
        },
        messageBox: {
            padding: '15px',
            marginBottom: '20px',
            borderRadius: '6px',
            backgroundColor: message.includes('Eroare') ? 'rgba(220, 53, 69, 0.2)' : 'rgba(40, 167, 69, 0.2)',
            color: message.includes('Eroare') ? '#ff6b6b' : '#28a745',
            textAlign: 'center',
            border: '1px solid currentcolor'
        }
    };

    if (loading) return <div style={{...styles.container, textAlign: 'center'}}>Se încarcă profilul...</div>;

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <button onClick={() => navigate('/events')} style={styles.backButton}>
                    &laquo; Înapoi la Evenimente
                </button>
                <h1 style={{margin: 0}}>Profilul Meu</h1>
                <div style={{width: '100px'}}></div>
            </div>

            {message && <div style={styles.messageBox}>{message}</div>}

            <div style={styles.contentGrid}>

                <div style={styles.card}>
                    <h2 style={styles.sectionTitle}>Date Personale</h2>
                    <form onSubmit={handleSaveProfile}>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Nume Complet</label>
                            <input
                                type="text"
                                style={styles.input}
                                value={profile.prenume_nume || ''}
                                onChange={e => setProfile({...profile, prenume_nume: e.target.value})}
                                placeholder="Ex: Ion Popescu"
                            />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Email</label>
                            <input
                                type="email"
                                style={styles.input}
                                value={profile.email || ''}
                                onChange={e => setProfile({...profile, email: e.target.value})}
                                disabled
                            />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Telefon</label>
                            <input
                                type="text"
                                style={styles.input}
                                value={profile.telefon || ''}
                                onChange={e => setProfile({...profile, telefon: e.target.value})}
                                placeholder="Ex: 0722..."
                            />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Data Nașterii</label>
                            <input
                                type="date"
                                style={styles.input}
                                value={profile.data_nasterii || ''}
                                onChange={e => setProfile({...profile, data_nasterii: e.target.value})}
                            />
                        </div>
                        <button type="submit" style={styles.saveButton}>
                            Salvează Modificările
                        </button>
                    </form>
                </div>

                <div style={styles.card}>
                    <h2 style={styles.sectionTitle}>Portofel Bilete </h2>

                    {tickets.length === 0 ? (
                        <p style={{color: '#888', textAlign: 'center', marginTop: '40px'}}>
                            Nu ai cumpărat niciun bilet încă.
                            <br/><br/>
                            <button
                                onClick={() => navigate('/events')}
                                style={{...styles.backButton, backgroundColor: '#ffc107', color: 'black'}}
                            >
                                Cumpără Acum
                            </button>
                        </p>
                    ) : (
                        <div style={{maxHeight: '500px', overflowY: 'auto', paddingRight: '5px'}}>
                            {tickets.map((t, idx) => (
                                <div key={idx} style={styles.ticketCard}>
                                    <div>
                                        <div style={{fontSize: '0.8rem', color: '#aaa', marginBottom: '2px'}}>COD BILET</div>
                                        <div style={styles.ticketCode}>{t.bilet?.cod || t.cod}</div>
                                        {t.bilet?.eveniment_id && (
                                            <div style={{fontSize: '0.8rem', color: '#aaa', marginTop: '5px'}}>
                                                Eveniment ID: #{t.bilet.eveniment_id}
                                            </div>
                                        )}
                                    </div>
                                    <div style={styles.badge}>ACTIV</div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default UserProfile;