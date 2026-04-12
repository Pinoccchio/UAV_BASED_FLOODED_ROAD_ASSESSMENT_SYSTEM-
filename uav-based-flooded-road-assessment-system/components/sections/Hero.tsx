"use client";

import { motion, type Variants } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

/* ---- Container variants ---- */
const containerVariants: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12 } },
};
const itemVariants: Variants = {
  hidden: { opacity: 0, y: 28 },
  visible: { opacity: 1, y: 0 },
};

/* ====================================================================
   MAIN HERO COMPONENT
   ==================================================================== */
export function Hero() {
  return (
    <section className="relative py-20 lg:py-32 overflow-hidden">
      {/* Subtle gradient background */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse 60% 50% at 50% 40%, var(--color-primary) / 0.05, transparent 70%)",
        }}
      />

      <div className="relative max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">

          {/* ---- LEFT COLUMN: Value Proposition ---- */}
          <div>
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="space-y-6"
            >
              {/* Project badge */}
              <motion.div variants={itemVariants}>
                <Badge variant="cyan" className="text-xs uppercase tracking-wide">
                  PLM BSECE Capstone 2025
                </Badge>
              </motion.div>

              {/* H1 — sentence case, professional */}
              <motion.h1
                variants={itemVariants}
                className="font-display font-bold tracking-tight"
              >
                <span className="block text-5xl sm:text-6xl lg:text-7xl text-foreground mb-2">
                  AI-powered flood road assessment
                </span>
              </motion.h1>

              {/* Subheadline */}
              <motion.p
                variants={itemVariants}
                className="text-xl text-muted-foreground leading-relaxed"
              >
                Automated UAV-based road passability classification for Philippine
                disaster response. Research prototype using deep learning.
              </motion.p>

              {/* CTAs */}
              <motion.div
                variants={itemVariants}
                className="flex flex-wrap gap-4 pt-2"
              >
                <Button size="lg" asChild>
                  <a href="#demo">Try the demo</a>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <a href="#how-it-works">How it works</a>
                </Button>
              </motion.div>

              {/* Stats row (static, no pulsing) */}
              <motion.div
                variants={itemVariants}
                className="grid grid-cols-3 gap-6 pt-8 border-t border-border"
              >
                <div>
                  <div className="text-2xl font-semibold text-primary mb-1">78.4%</div>
                  <div className="text-sm text-muted-foreground">Test accuracy (US data)</div>
                </div>
                <div>
                  <div className="text-2xl font-semibold text-primary mb-1">~2-3s</div>
                  <div className="text-sm text-muted-foreground">Processing time</div>
                </div>
                <div>
                  <div className="text-2xl font-semibold text-primary mb-1">3-Class</div>
                  <div className="text-sm text-muted-foreground">Classification</div>
                </div>
              </motion.div>
            </motion.div>
          </div>

          {/* ---- RIGHT COLUMN: Static visual ---- */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="rounded-lg border border-border bg-card shadow-lg overflow-hidden">
              {/* Header */}
              <div className="px-4 py-3 border-b border-border bg-card/50">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Classification system</span>
                  <Badge variant="default" className="text-xs">Prototype</Badge>
                </div>
              </div>

              {/* Classification levels showcase */}
              <div className="p-6 space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 rounded-md border border-[var(--status-passable)]/30 bg-[var(--status-passable)]/5">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-[var(--status-passable)]" />
                      <span className="font-medium text-sm">Passable</span>
                    </div>
                    <span className="text-xs text-muted-foreground">All vehicles allowed</span>
                  </div>

                  <div className="flex items-center justify-between p-3 rounded-md border border-[var(--status-limited)]/30 bg-[var(--status-limited)]/5">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-[var(--status-limited)]" />
                      <span className="font-medium text-sm">Limited passability</span>
                    </div>
                    <span className="text-xs text-muted-foreground">High-clearance only</span>
                  </div>

                  <div className="flex items-center justify-between p-3 rounded-md border border-[var(--status-impassable)]/30 bg-[var(--status-impassable)]/5">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-[var(--status-impassable)]" />
                      <span className="font-medium text-sm">Impassable</span>
                    </div>
                    <span className="text-xs text-muted-foreground">Road closed</span>
                  </div>
                </div>

                {/* Technology note */}
                <div className="pt-4 border-t border-border">
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    EfficientNet-B0 CNN model trained on aerial flood imagery.
                    Includes safety-enhanced predictions for emergency response.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
