import { Sparkles, Shield, Zap, Users, Palette, Smartphone } from "lucide-react";

const features = [
  {
    icon: Sparkles,
    title: "AI-Powered Styling",
    description: "Advanced machine learning algorithms analyze your body type, skin tone, and style preferences for personalized recommendations."
  },
  {
    icon: Zap,
    title: "Instant Results",
    description: "Get realistic virtual try-on results in seconds, not minutes. No waiting, just immediate style transformation."
  },
  {
    icon: Shield,
    title: "Privacy First",
    description: "Your photos are processed securely and never stored. We prioritize your privacy with end-to-end encryption."
  },
  {
    icon: Users,
    title: "Style Community",
    description: "Connect with fashion enthusiasts, share your virtual outfits, and get feedback from our style community."
  },
  {
    icon: Palette,
    title: "Color Matching",
    description: "Our AI analyzes your skin tone and suggests the most flattering colors and styles for your unique complexion."
  },
  {
    icon: Smartphone,
    title: "Mobile Optimized",
    description: "Perfect experience on any device. Take photos with your phone and get instant styling suggestions anywhere."
  }
];

export const Features = () => {
  return (
    <section className="py-24 bg-background">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6">
            Why Choose <span className="text-primary">Closetly.ai</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Experience the future of fashion with our innovative AI-powered virtual styling platform
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="group p-8 rounded-2xl bg-card hover:shadow-elegant transition-all duration-300 animate-fade-in border border-border/50 hover:border-primary/20"
              style={{animationDelay: `${index * 0.1}s`}}
            >
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 rounded-xl bg-gradient-primary flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300">
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-foreground">
                  {feature.title}
                </h3>
              </div>
              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};