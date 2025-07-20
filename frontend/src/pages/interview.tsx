import React from 'react';
import { useNavigate } from 'react-router-dom';

const Interview: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <h1>Interview Page</h1>
      <button
        style={{ marginTop: 24, padding: '12px 32px', fontSize: 18, borderRadius: 8, background: '#222', color: '#fff', border: 'none', cursor: 'pointer' }}
        onClick={() => navigate('/take_photo')}
      >
        Next
      </button>
    </div>
  );
};

export default Interview; 