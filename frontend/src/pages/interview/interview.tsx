import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles, Home, AlertCircle, CheckCircle } from "lucide-react";
import { InterviewAPI, INTERVIEW_FLOW_ID } from "./api/api";

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
        setError(response.error || "Failed to create interview");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    navigate("/take_photo");
  };

  return (
    <div className="min-h-screen bg-gradient-background relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-glow/30 rounded-full blur-3xl animate-float"></div>
        <div
          className="absolute bottom-20 right-10 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "1.5s" }}
        ></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 animate-fade-in">
          <Button
            variant="glass"
            onClick={() => navigate("/")}
            className="flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            Back to Home
          </Button>

          <div className="flex items-center gap-2 text-white">
            <Sparkles className="w-5 h-5 text-primary-glow" />
            <h1 className="text-xl font-semibold">Style Interview</h1>
          </div>

        </div>

        {/* Main Content */}
        <div className="max-w-[95%] w-[95%] mx-auto">
          <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white mb-8 w-full">
            <CardHeader>
              <CardTitle className="text-center text-3xl font-bold text-white mb-2">
                Start Your Style Interview
              </CardTitle>
              <p className="text-center text-white/80 text-lg">
                Begin your personalized styling consultation
              </p>
            </CardHeader>
            <CardContent className="p-8">
              {!interviewUrl && (
                <div className="flex flex-col items-center justify-center space-y-6">
                  <Button
                    variant="hero"
                    size="lg"
                    onClick={createInterview}
                    disabled={loading}
                    className="w-full max-w-xs"
                  >
                    {loading ? "Creating Interview..." : "Start Interview"}
                  </Button>
                  {error && (
                    <div className="flex items-center gap-2 bg-red-100/80 text-red-700 px-4 py-2 rounded-lg border border-red-200 animate-shake">
                      <AlertCircle className="w-5 h-5" />
                      <span>Error: {error}</span>
                    </div>
                  )}
                </div>
              )}

              {interviewUrl && (
                <div className="w-full max-w-5xl mx-auto">
                  <div className="flex flex-col md:flex-row items-center justify-between mb-4 gap-4">
                    <h3 className="text-lg font-semibold text-white mb-0">Your Interview Session</h3>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={handleNext}
                      className="flex items-center gap-2"
                    >
                      Continue to Photo <Sparkles className="w-4 h-4" />
                    </Button>
                  </div>
                  {interviewId && (
                    <p className="text-xs text-white/70 mb-2">Interview ID: {interviewId}</p>
                  )}
                  <div className="rounded-2xl overflow-hidden border-2 border-white/20 shadow-lg bg-black/30">
                    <iframe
                      src={interviewUrl}
                      className="w-full h-[75vh] min-h-[500px] border-0 rounded-2xl"
                      style={{ minHeight: '500px', height: '75vh' }}
                      title="Style Interview"
                      allow="camera; microphone; autoplay"
                      allowFullScreen
                    />
                  </div>
              
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Interview;
