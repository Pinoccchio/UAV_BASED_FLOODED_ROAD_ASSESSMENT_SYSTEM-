"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Plane, Camera, Brain, Map } from "lucide-react";

const steps = [
  {
    number: 1,
    icon: Plane,
    title: "Deploy UAV",
    description:
      "A UAV/drone is deployed over flooded road networks to systematically capture aerial imagery of affected areas, supporting common drone camera output formats.",
  },
  {
    number: 2,
    icon: Camera,
    title: "Capture imagery",
    description:
      "The UAV camera captures downward imagery of flooded roads. GPS metadata is embedded in each frame for precise geolocation tagging and road segment mapping.",
  },
  {
    number: 3,
    icon: Brain,
    title: "AI analyzes",
    description:
      "A CNN-based classification model (EfficientNet-B0) processes each image through preprocessing, feature extraction, and multi-class classification to assess road passability.",
  },
  {
    number: 4,
    icon: Map,
    title: "View results",
    description:
      "Classified road segments populate a map dashboard with color-coded passability overlays. Supports NDRRMC, DPWH, and local DRRMO offices with near-real-time passability data for dispatch decisions.",
  },
];

export function HowItWorks() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="how-it-works" className="relative py-20 lg:py-28">
      <div ref={ref} className="max-w-4xl mx-auto px-6 sm:px-8 lg:px-12">
        {/* Header */}
        <motion.div
          className="mb-12 space-y-3"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <h2 className="font-display text-3xl lg:text-4xl font-semibold">
            How it works
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl">
            From UAV deployment to passability classification — a four-stage
            pipeline delivering near real-time assessments during the critical
            post-disaster response window.
          </p>
        </motion.div>

        {/* Vertical timeline */}
        <div className="relative">
          {/* Vertical connecting line */}
          <div className="absolute left-6 top-0 bottom-0 w-px bg-border" />

          {/* Steps */}
          <div className="space-y-12">
            {steps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={step.number}
                  className="relative flex gap-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={inView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.5, delay: idx * 0.15 }}
                >
                  {/* Icon circle */}
                  <div className="relative z-10 flex-shrink-0 w-12 h-12 rounded-full bg-primary flex items-center justify-center text-white">
                    <Icon size={20} strokeWidth={2} />
                  </div>

                  {/* Content */}
                  <div className="flex-1 pt-1 pb-4">
                    <h3 className="text-xl font-semibold mb-2">
                      {step.title}
                    </h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
