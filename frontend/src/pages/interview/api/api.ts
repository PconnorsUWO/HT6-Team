// Interview API module for interacting with backend interview routes

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
const INTERVIEW_API_BASE = `${API_BASE_URL}/api/interview`;
export const INTERVIEW_FLOW_ID = 'b8a864c5';

// Type definitions
export interface InterviewFlowData {
  org_name: string;
  title: string;
  questions: string[];
  interview_type?: string;
  voice_id?: string;
  language?: string;
  company_logo_url?: string;
  additional_info?: string;
  is_video_enabled?: boolean;
  is_phone_call_enabled?: boolean;
  is_doc_upload_enabled?: boolean;
  redirect_url?: string;
  webhook_url?: string;
}

export interface InterviewConfigData {
  interview_flow_id: string;
  interviewee_email_address?: string;
  interviewee_first_name?: string;
  interviewee_last_name?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  error?: string;
  data?: T;
}

export interface InterviewFlowResponse extends ApiResponse {
  flow_id?: string;
}

export interface InterviewResponse extends ApiResponse {
  interview_id?: string;
  interview_link?: string;
}

export interface InterviewStatusResponse extends ApiResponse {
  interview_id?: string;
  status?: string;
}

export interface InterviewTranscriptResponse extends ApiResponse {
  interview_id?: string;
  transcript?: string;
}

export interface InterviewAudioResponse extends ApiResponse {
  interview_id?: string;
  audio_url?: string;
}

export interface QuickFlowResponse extends ApiResponse {
  template?: string;
  flow_id?: string;
}

export interface TemplatesResponse extends ApiResponse {
  template?: {
    [key: string]: {
      name: string;
      description: string;
      question_count: number;
      type: string;
    };
  };
}

// API class for interview operations
export class InterviewAPI {
  private static async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${INTERVIEW_API_BASE}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Create a new interview flow
   */
  static async createInterviewFlow(data: InterviewFlowData): Promise<InterviewFlowResponse> {
    return this.makeRequest('/create-flow', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Create a new interview from an existing flow
   */
  static async createInterview(data: InterviewConfigData): Promise<InterviewResponse> {
    return this.makeRequest('/create-interview', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Get interview details and results
   */
  static async getInterview(interviewId: string): Promise<ApiResponse> {
    return this.makeRequest(`/interview/${interviewId}`);
  }

  /**
   * Get interview status
   */
  static async getInterviewStatus(interviewId: string): Promise<InterviewStatusResponse> {
    return this.makeRequest(`/interview/${interviewId}/status`);
  }

  /**
   * Get interview transcript
   */
  static async getInterviewTranscript(interviewId: string): Promise<InterviewTranscriptResponse> {
    return this.makeRequest(`/interview/${interviewId}/transcript`);
  }

  /**
   * Get interview audio URL
   */
  static async getInterviewAudio(interviewId: string): Promise<InterviewAudioResponse> {
    return this.makeRequest(`/interview/${interviewId}/audio`);
  }

  /**
   * Create a quick stylist consultation flow
   */
  static async createQuickFlow(orgName?: string): Promise<QuickFlowResponse> {
    const data = orgName ? { org_name: orgName } : {};
    return this.makeRequest('/quick-flow', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Get available interview templates
   */
  static async getAvailableTemplates(): Promise<TemplatesResponse> {
    return this.makeRequest('/templates');
  }
}

// Helper functions for common operations
export const interviewHelpers = {
  /**
   * Create a complete interview flow and interview in one call
   */
  async createFullInterview(
    flowData: InterviewFlowData,
    intervieweeData?: Omit<InterviewConfigData, 'interview_flow_id'>
  ): Promise<{ flow: InterviewFlowResponse; interview?: InterviewResponse }> {
    const flowResponse = await InterviewAPI.createInterviewFlow(flowData);
    
    if (!flowResponse.success || !flowResponse.flow_id) {
      throw new Error(flowResponse.error || 'Failed to create interview flow');
    }

    let interviewResponse: InterviewResponse | undefined;
    
    if (intervieweeData) {
      interviewResponse = await InterviewAPI.createInterview({
        interview_flow_id: flowResponse.flow_id,
        ...intervieweeData,
      });
    }

    return {
      flow: flowResponse,
      interview: interviewResponse,
    };
  },

  /**
   * Poll interview status until completion
   */
  async pollInterviewStatus(
    interviewId: string,
    intervalMs: number = 5000,
    timeoutMs: number = 300000 // 5 minutes
  ): Promise<string> {
    const startTime = Date.now();
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          if (Date.now() - startTime > timeoutMs) {
            reject(new Error('Polling timeout reached'));
            return;
          }

          const statusResponse = await InterviewAPI.getInterviewStatus(interviewId);
          
          if (!statusResponse.success) {
            reject(new Error(statusResponse.error || 'Failed to get status'));
            return;
          }

          const status = statusResponse.status;
          
          if (status === 'completed' || status === 'failed') {
            resolve(status);
            return;
          }

          setTimeout(poll, intervalMs);
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  },

  /**
   * Get complete interview results (transcript + audio)
   */
  async getCompleteResults(interviewId: string): Promise<{
    transcript?: string;
    audioUrl?: string;
    status: string;
  }> {
    const [statusResponse, transcriptResponse, audioResponse] = await Promise.allSettled([
      InterviewAPI.getInterviewStatus(interviewId),
      InterviewAPI.getInterviewTranscript(interviewId),
      InterviewAPI.getInterviewAudio(interviewId),
    ]);

    const status = statusResponse.status === 'fulfilled' 
      ? statusResponse.value.status || 'unknown'
      : 'error';

    const transcript = transcriptResponse.status === 'fulfilled' 
      ? transcriptResponse.value.transcript 
      : undefined;

    const audioUrl = audioResponse.status === 'fulfilled' 
      ? audioResponse.value.audio_url 
      : undefined;

    return { transcript, audioUrl, status };
  },
};

// Export default instance for convenience
export default InterviewAPI;