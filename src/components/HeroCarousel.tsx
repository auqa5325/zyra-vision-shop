import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import heroWearables from "@/assets/hero-wearables.jpg";
import heroElectronics from "@/assets/hero-electronics.jpg";
import heroDeals from "@/assets/hero-deals.jpg";

const slides = [
  {
    id: 1,
    image: heroWearables,
    title: "Smart Wearables",
    subtitle: "Track your fitness journey",
    cta: "Shop Now",
  },
  {
    id: 2,
    image: heroElectronics,
    title: "Latest Electronics",
    subtitle: "Premium gadgets at your fingertips",
    cta: "Explore",
  },
  {
    id: 3,
    image: heroDeals,
    title: "Trending Deals",
    subtitle: "Up to 50% off on selected items",
    cta: "View Deals",
  },
];

export const HeroCarousel = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000);

    return () => clearInterval(timer);
  }, []);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  return (
    <section className="relative w-full h-[400px] md:h-[500px] overflow-hidden rounded-2xl">
      {/* Slides */}
      {slides.map((slide, index) => (
        <div
          key={slide.id}
          className={`absolute inset-0 transition-opacity duration-700 ${
            index === currentSlide ? "opacity-100" : "opacity-0"
          }`}
        >
          <img
            src={slide.image}
            alt={slide.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-black/30 to-transparent" />
          
          {/* Content */}
          <div className="absolute inset-0 flex flex-col justify-center px-8 md:px-16 max-w-2xl">
            <h2 className="text-4xl md:text-6xl font-bold text-white mb-4 animate-fade-in-up">
              {slide.title}
            </h2>
            <p className="text-lg md:text-xl text-white/90 mb-6 animate-fade-in-up">
              {slide.subtitle}
            </p>
            <div className="animate-fade-in-up">
              <Button variant="hero" size="lg">
                {slide.cta}
              </Button>
            </div>
          </div>
        </div>
      ))}

      {/* Navigation Arrows */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/10 hover:bg-white/20 text-white backdrop-blur-sm"
        onClick={prevSlide}
      >
        <ChevronLeft className="h-6 w-6" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/10 hover:bg-white/20 text-white backdrop-blur-sm"
        onClick={nextSlide}
      >
        <ChevronRight className="h-6 w-6" />
      </Button>

      {/* Dots Indicator */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
        {slides.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={`h-2 rounded-full transition-all ${
              index === currentSlide
                ? "w-8 bg-white"
                : "w-2 bg-white/50 hover:bg-white/75"
            }`}
          />
        ))}
      </div>
    </section>
  );
};
