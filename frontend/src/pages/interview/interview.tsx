import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { InterviewAPI, INTERVIEW_FLOW_ID } from './api/api';

const Interview: React.FC = () => {
  const navigate = useNavigate();
  const [interviewUrl, setInterviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [interviewId, setInterviewId] = useState<string | null>(null);

  const createInterview = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await InterviewAPI.createInterview({
        interview_flow_id: INTERVIEW_FLOW_ID,
      });

      if (response.success && response.interview_link) {
        setInterviewUrl(response.interview_link);
        setInterviewId(response.interview_id || null);
      } else {
        setError(response.error || 'Failed to create interview');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    navigate('/take_photo');
  };

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '100vh',
      padding: '20px',
      backgroundColor: '#f5f5f5'
    }}>
      <h1 style={{ marginBottom: '30px', color: '#333' }}>Style Interview</h1>
      
      {!interviewUrl && (
        <div style={{ textAlign: 'center' }}>
          <p style={{ marginBottom: '20px', color: '#666' }}>
            Start your personalized styling consultation
          </p>
          <button
            style={{ 
              padding: '12px 32px', 
              fontSize: 18, 
              borderRadius: 8, 
              background: loading ? '#ccc' : '#007bff', 
              color: '#fff', 
              border: 'none', 
              cursor: loading ? 'not-allowed' : 'pointer',
              marginBottom: '20px'
            }}
            onClick={createInterview}
            disabled={loading}
          >
            {loading ? 'Creating Interview...' : 'Start Interview'}
          </button>
        </div>
      )}

      {error && (
        <div style={{ 
          backgroundColor: '#fee', 
          color: '#c33', 
          padding: '12px', 
          borderRadius: '8px', 
          marginBottom: '20px',
          border: '1px solid #fcc'
        }}>
          Error: {error}
        </div>
      )}

      {interviewUrl && (
        <div style={{ width: '100%', maxWidth: '1200px', height: '80vh' }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: '15px' 
          }}>
            <h3 style={{ margin: 0, color: '#333' }}>Your Interview Session</h3>
            <button
              style={{ 
                padding: '8px 16px', 
                fontSize: 14, 
                borderRadius: 6, 
                background: '#28a745', 
                color: '#fff', 
                border: 'none', 
                cursor: 'pointer'
              }}
              onClick={handleNext}
            >
              Continue to Photo →
            </button>
          </div>
          
          {interviewId && (
            <p style={{ 
              fontSize: '12px', 
              color: '#666', 
              marginBottom: '10px' 
            }}>
              Interview ID: {interviewId}
            </p>
          )}
          
          <iframe
            src={interviewUrl}
            style={{
              width: '100%',
              height: '100%',
              border: '2px solid #ddd',
              borderRadius: '12px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
            }}
            title="Style Interview"
            allow="camera; microphone; autoplay"
            allowFullScreen
          />
        </div>
      )}
    </div>
  );
};

export default Interview; 