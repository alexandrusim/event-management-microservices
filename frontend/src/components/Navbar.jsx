import { Link } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const Navbar = () => {
    const { user, logout } = useContext(AuthContext);

    return (
        <nav style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '1rem 2rem',
            backgroundColor: '#333',
            color: 'white'
        }}>
            <div className="logo">
                <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold', fontSize: '1.2rem' }}>
                    Event Manager
                </Link>
            </div>

            <div className="links">
                {user ? (
                    <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
                        <span>Salut, {user.role === 'admin' ? 'Admin' : 'User'}!</span>
                        <Link to="/profile" style={{ color: '#ddd' }}>Profil</Link>
                        <button
                            onClick={logout}
                            style={{ padding: '5px 10px', cursor: 'pointer', backgroundColor: '#d9534f', color: 'white', border: 'none' }}
                        >
                            Logout
                        </button>
                    </div>
                ) : (
                    <Link to="/login" style={{ color: 'white', textDecoration: 'none', border: '1px solid white', padding: '5px 10px' }}>
                        Autentificare
                    </Link>
                )}
            </div>
        </nav>
    );
};

export default Navbar;