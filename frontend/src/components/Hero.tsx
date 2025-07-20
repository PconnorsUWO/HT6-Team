import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";

export const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="min-h-screen bg-gradient-background flex items-center justify-center relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-glow/30 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-float" style={{animationDelay: '1.5s'}}></div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">
        <div className="animate-fade-in">
          <div className="flex items-center justify-center mb-6">
            <Sparkles className="h-8 w-8 text-primary-glow mr-3 animate-float" />
            <span className="text-primary-glow font-semibold tracking-wider uppercase text-sm">
              AI-Powered Virtual Styling
            </span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Try On Any Outfit
            <span className="block bg-gradient-to-r from-primary-glow to-white bg-clip-text text-transparent">
              Instantly
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-200 mb-8 max-w-2xl mx-auto leading-relaxed">
            Take a photo, describe what you want, and watch our AI create the perfect virtual try-on experience with personalized style recommendations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button variant="hero" size="lg" className="text-lg px-8 py-4" onClick={() => navigate('/interview')}>
              Start Your Style Journey
              <ArrowRight className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
            
      {/* Floating Elements */}
      <div className="absolute top-20 left-10 w-4 h-4 bg-primary-glow rounded-full opacity-60 animate-float"></div>
      <div className="absolute bottom-20 right-10 w-6 h-6 bg-primary rounded-full opacity-40 animate-float" style={{animationDelay: '1s'}}></div>
      <div className="absolute top-1/2 left-20 w-3 h-3 bg-white rounded-full opacity-30 animate-float" style={{animationDelay: '2s'}}></div>

    </section>
  );
};
