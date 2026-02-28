import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../services/api';

const EventForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const isEditMode = !!id;

    const [formData, setFormData] = useState({
        nume: '',
        locatie: '',
        descriere: '',
        numarLocuri: 100
    });
    const [error, setError] = useState('');

    useEffect(() => {
        if (isEditMode) {
            const fetchEvent = async () => {
                try {
                    const response = await api.get(`/api/event-manager/events/${id}`);
                    const e = response.data.event;
                    setFormData({
                        nume: e.nume,
                        locatie: e.locatie,
                        descriere: e.descriere,
                        numarLocuri: e.numarLocuri
                    });
                } catch (err) {
                    setError("Nu s-au putut incarca datele evenimentului.");
                }
            };
            fetchEvent();
        }
    }, [id, isEditMode]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            if (isEditMode) {
                await api.put(`/api/event-manager/events/${id}`, formData);
                alert("Eveniment actualizat!");
            } else {
                await api.post('/api/event-manager/events', formData);
                alert("Eveniment creat!");
            }
            navigate('/');
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "Eroare la salvare.");
        }
    };

    return (
        <div style={{ maxWidth: '500px', margin: '30px auto', padding: '20px', border: '1px solid #ccc' }}>
            <h2>{isEditMode ? 'Editeaza Eveniment' : 'Creeaza Eveniment Nou'}</h2>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            <form onSubmit={handleSubmit}>
                <div style={{marginBottom: '15px'}}>
                    <label>Nume Eveniment:</label>
                    <input
                        type="text"
                        value={formData.nume}
                        onChange={(e) => setFormData({...formData, nume: e.target.value})}
                        required
                        style={{width: '100%', padding: '8px'}}
                    />
                </div>

                <div style={{marginBottom: '15px'}}>
                    <label>Locație:</label>
                    <input
                        type="text"
                        value={formData.locatie}
                        onChange={(e) => setFormData({...formData, locatie: e.target.value})}
                        required
                        style={{width: '100%', padding: '8px'}}
                    />
                </div>

                <div style={{marginBottom: '15px'}}>
                    <label>Număr Locuri:</label>
                    <input
                        type="number"
                        value={isNaN(formData.numarLocuri) ? '' : formData.numarLocuri}
                        onChange={(e) => {
                            const val = e.target.value;
                            setFormData({...formData, numarLocuri: val === '' ? '' : parseInt(val)});
                        }}
                        required
                        min="1"
                        style={{width: '100%', padding: '8px'}}
                    />
                </div>

                <div style={{marginBottom: '15px'}}>
                    <label>Descriere:</label>
                    <textarea
                        value={formData.descriere}
                        onChange={(e) => setFormData({...formData, descriere: e.target.value})}
                        required
                        rows="4"
                        style={{width: '100%', padding: '8px'}}
                    />
                </div>

                <button type="submit" style={{
                    padding: '10px 20px',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    cursor: 'pointer'
                }}>
                    {isEditMode ? 'Salveaza Modificarile' : 'Creeaza Eveniment'}
                </button>
            </form>
        </div>
    );
};

export default EventForm;