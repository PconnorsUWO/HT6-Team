import React from 'react';
import { useNavigate } from 'react-router-dom';

const TakePhoto: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <h1>Take Photo Page</h1>
      <button
        style={{ marginTop: 24, padding: '12px 32px', fontSize: 18, borderRadius: 8, background: '#222', color: '#fff', border: 'none', cursor: 'pointer' }}
        onClick={() => navigate('/final')}
      >
        Next
      </button>
    </div>
  );
};

export default TakePhoto; 