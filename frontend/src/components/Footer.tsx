import { Heart, Instagram, Twitter, Youtube } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="bg-foreground text-background py-16">
      <div className="max-w-6xl mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div className="col-span-2">
            <h3 className="text-2xl font-bold mb-4 flex items-center">
              <span className="text-primary-glow">Closetly</span>.ai
            </h3>
            <p className="text-gray-300 mb-6 max-w-md">
              The world's most advanced AI virtual stylist. Find the perfect outfit for any occasion.
            </p>
            <div className="flex space-x-4">
              <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center hover:bg-primary/30 transition-colors cursor-pointer">
                <Instagram className="h-5 w-5 text-primary-glow" />
              </div>
              <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center hover:bg-primary/30 transition-colors cursor-pointer">
                <Twitter className="h-5 w-5 text-primary-glow" />
              </div>
              <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center hover:bg-primary/30 transition-colors cursor-pointer">
                <Youtube className="h-5 w-5 text-primary-glow" />
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-gray-300">
              <li><a href="#" className="hover:text-primary-glow transition-colors">Virtual Try-On</a></li>
              <li><a href="#" className="hover:text-primary-glow transition-colors">Style Recommendations</a></li>
              <li><a href="#" className="hover:text-primary-glow transition-colors">Color Analysis</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-gray-300">
              <li><a href="#" className="hover:text-primary-glow transition-colors">About Us</a></li>
              <li><a href="#" className="hover:text-primary-glow transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-primary-glow transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-primary-glow transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-700 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm flex items-center mt-4 md:mt-0">
            Made with <Heart className="h-4 w-4 text-primary-glow mx-1" /> for fashion lovers
          </p>
        </div>
      </div>
    </footer>
  );
};