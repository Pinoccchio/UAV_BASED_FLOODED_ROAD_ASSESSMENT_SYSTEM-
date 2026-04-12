"use client";

import { useRef } from "react";
import { motion, useInView, type Variants } from "framer-motion";
import { Brain, Zap, Plane, Map, Truck, Check } from "lucide-react";

// Primary feature
const primaryFeature = {
  icon: Brain,
  title: "CNN-based classification",
  description:
    "EfficientNet-B0 model classifies roads into 3 passability levels (Passable, Limited Passability, Impassable) based on aerial imagery. Trained with safety-enhanced predictions for disaster response.",
  benefits: [
    "79.6% test accuracy (US data)",
    "Safety-enhanced predictions",
    "Near real-time processing (~2-3s)",
  ],
};

// Supporting features
const supportingFeatures = [
  {
    icon: Plane,
    title: "UAV integration",
    description:
      "Supports aerial image capture from drone platforms with GPS tagging and image preprocessing for flood detection.",
  },
  {
    icon: Map,
    title: "Map visualization",
    description:
      "GPS-tagged road segments displayed on interactive maps with color-coded passability overlays for command centers.",
  },
  {
    icon: Truck,
    title: "Vehicle recommendations",
    description:
      "Three-class output maps directly to vehicle type recommendations, guiding safe passage for different vehicle types.",
  },
  {
    icon: Zap,
    title: "Multi-scenario support",
    description:
      "Model validated across typhoon, monsoon, and flash flood scenarios common to Philippine road networks.",
  },
];

const containerVariants: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
};

export function Features() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="features" className="relative py-20 lg:py-28">
      <div ref={ref} className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        {/* Section header */}
        <motion.div
          className="mb-12 space-y-3"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <h2 className="font-display text-3xl lg:text-4xl font-semibold">
            Core capabilities
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl">
            Deep learning-powered assessment for disaster response
          </p>
        </motion.div>

        {/* Primary Feature (large card) */}
        <motion.div
          className="mb-8 p-8 border border-border rounded-lg bg-card shadow-sm hover:shadow-md transition-shadow"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 rounded-md bg-primary/10 border border-primary/20 flex items-center justify-center">
              <primaryFeature.icon size={24} className="text-primary" strokeWidth={1.5} />
            </div>
            <div className="flex-1">
              <h3 className="text-2xl font-semibold mb-2">
                {primaryFeature.title}
              </h3>
              <p className="text-muted-foreground mb-4 leading-relaxed">
                {primaryFeature.description}
              </p>
              <div className="flex flex-wrap gap-4 text-sm">
                {primaryFeature.benefits.map((benefit) => (
                  <span key={benefit} className="flex items-center gap-2">
                    <Check size={16} className="text-[var(--status-passable)]" strokeWidth={2} />
                    <span>{benefit}</span>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Supporting Features (2x2 grid) */}
        <motion.div
          className="grid md:grid-cols-2 gap-6"
          variants={containerVariants}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
        >
          {supportingFeatures.map((feature) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                variants={cardVariants}
                className="p-6 border border-border rounded-lg bg-card shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className="flex-shrink-0 w-10 h-10 rounded-md bg-primary/5 border border-primary/10 flex items-center justify-center">
                    <Icon size={20} className="text-primary" strokeWidth={1.5} />
                  </div>
                  <h4 className="text-lg font-medium pt-1">
                    {feature.title}
                  </h4>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
