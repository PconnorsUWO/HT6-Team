import { Camera, Zap, Heart } from "lucide-react";
import stepPhoto from "@/assets/step-photo.jpg";
import stepAI from "@/assets/step-ai.jpg";
import stepResults from "@/assets/step-results.jpg";

const steps = [
  {
    icon: Camera,
    title: "Take Your Photo",
    description: "Upload a clear photo of yourself in good lighting. Our AI works best with front-facing photos.",
    image: stepPhoto,
    color: "from-primary to-primary-glow"
  },
  {
    icon: Zap,
    title: "Select Clothing",
    description: "Browse our extensive catalog or upload your own clothing items to try on virtually.",
    image: stepAI,
    color: "from-primary-glow to-primary"
  },
  {
    icon: Heart,
    title: "Get Styled",
    description: "Receive your personalized virtual try-on with AI-powered style recommendations and feedback.",
    image: stepResults,
    color: "from-primary to-primary-dark"
  }
];

export const HowItWorks = () => {
  return (
    <section className="py-24 bg-gradient-subtle">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6">
            How It <span className="text-primary">Works</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            wardrobe.ai will transform your style experience in just three simple steps with our cutting-edge AI technology
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div 
              key={index} 
              className="group text-center animate-fade-in hover:scale-105 transition-all duration-300"
              style={{animationDelay: `${index * 0.2}s`}}
            >
              <div className="relative mb-8">
                <div className="w-full h-64 rounded-2xl overflow-hidden shadow-elegant mb-6">
                  <img 
                    src={step.image} 
                    alt={step.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                </div>
                
                <div className={`absolute -bottom-4 left-1/2 transform -translate-x-1/2 w-16 h-16 rounded-full bg-gradient-to-r ${step.color} flex items-center justify-center shadow-glow`}>
                  <step.icon className="h-8 w-8 text-white" />
                </div>
              </div>
              
              <div className="pt-8">
                <h3 className="text-2xl font-bold text-foreground mb-4">
                  {step.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};