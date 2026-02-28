import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { useContext } from 'react';

import Login from './pages/Login';
import EventList from './pages/EventList';
import EventForm from './pages/EventForm';
import EventAttendees from './pages/EventAttendees';
import UserProfile from './pages/UserProfile';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) return <div>Loading...</div>;
  return user ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/events" replace />} />

          <Route path="/events" element={<EventList />} />

          <Route path="/login" element={<Login />} />

          <Route path="/events/new" element={
            <PrivateRoute>
              <EventForm />
            </PrivateRoute>
          } />

          <Route path="/events/edit/:id" element={
            <PrivateRoute>
              <EventForm />
            </PrivateRoute>
          } />

          <Route path="/events/:id/attendees" element={
             <PrivateRoute>
              <EventAttendees />
             </PrivateRoute>
          } />

          <Route path="/profile" element={
            <PrivateRoute>
                <UserProfile />
            </PrivateRoute>
          } />

          <Route path="*" element={<Navigate to="/events" replace />} />

        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;