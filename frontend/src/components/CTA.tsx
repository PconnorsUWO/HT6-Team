import { Button } from "@/components/ui/button";
import { ArrowRight, Star } from "lucide-react";

export const CTA = () => {
  return (
    <section className="py-24 bg-gradient-hero relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-20 w-32 h-32 bg-primary-glow/20 rounded-full blur-xl"></div>
        <div className="absolute bottom-20 right-20 w-48 h-48 bg-primary/20 rounded-full blur-2xl"></div>
      </div>
      
      <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">
        <div className="animate-fade-in">
          <div className="flex items-center justify-center mb-6">
            <Star className="h-6 w-6 text-primary-glow mr-2" />
            <Star className="h-6 w-6 text-primary-glow mr-2" />
            <Star className="h-6 w-6 text-primary-glow mr-2" />
            <Star className="h-6 w-6 text-primary-glow mr-2" />
            <Star className="h-6 w-6 text-primary-glow" />
          </div>
          
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Ready to Transform
            <span className="block text-primary-glow">Your Style?</span>
          </h2>
          
          <p className="text-xl text-black-200 mb-8 max-w-2xl mx-auto">
            Join thousands of fashion-forward individuals who have revolutionized their style with wardrobe.ai
          </p>
        </div>
      </div>
    </section>
  );
};