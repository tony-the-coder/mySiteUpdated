import React from 'react';
import { motion } from 'motion';
import { cn } from '../lib/utils';

interface BouncingTextHeroProps {
  title: string;
  subtitle: string;
  className?: string;
}

const BouncingTextHero: React.FC<BouncingTextHeroProps> =
    ({ title, subtitle, className }) => {
  // A simple animation example using motion (framer-motion)
  const variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <section className={cn(
      "relative min-h-[50vh] flex items-center justify-center bg-brand-charcoal-darker overflow-hidden",
      className
    )}>
      {/* Background Aurora Effect from your original partial */}
      <div
        className="absolute inset-0 z-0 transition-opacity duration-500 opacity-50"
        style={{
          backgroundImage: `radial-gradient(at 27% 37%, hsla(215, 98%, 61%, 0.3) 0px, transparent 50%), radial-gradient(at 77% 42%, hsla(193, 98%, 61%, 0.3) 0px, transparent 50%)`,
        }}
      ></div>

      <div className="relative z-10 text-center text-white px-6 py-20">
        <motion.h1
          initial="hidden"
          animate="visible"
          transition={{ duration: 0.8 }}
          variants={variants}
          className="text-4xl md:text-6xl font-bold font-heading !text-white"
        >
          {title}
        </motion.h1>

        <motion.p
          initial="hidden"
          animate="visible"
          transition={{ duration: 0.8, delay: 0.3 }}
          variants={variants}
          className="mt-4 text-lg md:text-xl max-w-2xl mx-auto text-gray-300"
        >
          {subtitle}
        </motion.p>
      </div>
    </section>
  );
};

export default BouncingTextHero;