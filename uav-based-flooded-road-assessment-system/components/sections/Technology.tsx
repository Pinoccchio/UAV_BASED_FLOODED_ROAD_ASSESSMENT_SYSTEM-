"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { ArrowRight } from "lucide-react";

const techCategories = [
  {
    title: "AI & machine learning",
    items: ["PyTorch Lightning", "EfficientNet-B0 CNN", "ONNX Runtime", "Backend API (Python)"],
  },
  {
    title: "Computer vision",
    items: ["OpenCV", "NumPy", "Pillow (PIL)", "Matplotlib"],
  },
  {
    title: "Web & visualization",
    items: ["Next.js", "React", "TypeScript", "Tailwind CSS", "Leaflet Maps"],
  },
];

const architectureSteps = [
  {
    label: "UAV capture",
    description: "Aerial imagery with GPS tagging",
  },
  {
    label: "Preprocessing",
    description: "OpenCV · NumPy · Augmentation",
  },
  {
    label: "CNN inference",
    description: "EfficientNet-B0 · 3-class output",
  },
  {
    label: "Map dashboard",
    description: "GPS-tagged road segments",
  },
];

export function Technology() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="technology" className="relative py-20 lg:py-28">
      <div ref={ref} className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        {/* Header */}
        <motion.div
          className="mb-12 space-y-3"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <h2 className="font-display text-3xl lg:text-4xl font-semibold">
            Technology stack
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl">
            Built on proven deep learning frameworks and optimized for real-world disaster response deployment.
          </p>
        </motion.div>

        {/* Dataset Context */}
        <motion.div
          className="mb-8 p-4 rounded-lg border border-blue-500/30 bg-blue-500/10"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <p className="text-sm text-blue-100">
            <strong>Dataset context:</strong> Model trained on US hurricane/flood imagery (RescueNet + FloodNet: 4,892 images).
            Performance on Philippine roads may vary (estimated 10-15% accuracy reduction due to domain shift).
          </p>
        </motion.div>

        {/* Architecture flow (full width top) */}
        <motion.div
          className="mb-12 p-6 border border-border rounded-lg bg-card shadow-sm"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h3 className="text-lg font-medium mb-6">System architecture</h3>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {architectureSteps.map((step, index) => (
              <div key={step.label} className="flex items-start gap-3">
                {index > 0 && (
                  <div className="hidden md:flex items-center flex-shrink-0 -ml-2 mr-1">
                    <ArrowRight size={16} className="text-primary" />
                  </div>
                )}
                <div className={index > 0 ? "flex-1" : "flex-1 md:ml-0"}>
                  <div className="font-medium text-sm mb-1">{step.label}</div>
                  <div className="text-xs text-muted-foreground leading-relaxed">
                    {step.description}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Tech stack (3 columns) */}
        <motion.div
          className="grid md:grid-cols-3 gap-6"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          {techCategories.map((category, idx) => (
            <motion.div
              key={category.title}
              className="p-6 border border-border rounded-lg bg-card shadow-sm"
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.3 + idx * 0.1 }}
            >
              <h4 className="text-lg font-medium mb-4">{category.title}</h4>
              <ul className="space-y-2">
                {category.items.map((item) => (
                  <li key={item} className="text-sm text-muted-foreground flex items-center gap-2">
                    <span className="w-1 h-1 rounded-full bg-primary flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
