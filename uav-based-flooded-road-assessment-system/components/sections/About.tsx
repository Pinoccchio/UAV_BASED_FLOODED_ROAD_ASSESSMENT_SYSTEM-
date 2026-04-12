"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";

const stats = [
  { value: "3", label: "Classification Classes", sub: "Passable · Limited Passability · Impassable" },
  { value: "20+", label: "Typhoons Annually", sub: "Philippine weather average" },
  { value: "79.6%", label: "Test Accuracy", sub: "On US flood data (target: 85%)" },
  { value: "72 HRS", label: "Critical Window", sub: "Post-disaster response" },
];

const stakeholders = [
  {
    abbr: "NDRRMC",
    name: "National Disaster Risk Reduction & Management Council",
    role: "National-level disaster command and response coordination",
    color: "oklch(0.72 0.22 200)",
  },
  {
    abbr: "DPWH",
    name: "Dept. of Public Works & Highways",
    role: "Road infrastructure assessment and repair prioritization",
    color: "oklch(0.75 0.22 68)",
  },
  {
    abbr: "LGU-DRRMOs",
    name: "Local Government Unit DRRMO Offices",
    role: "Barangay-level evacuation routing and resource dispatch",
    color: "oklch(0.70 0.22 145)",
  },
];

const impactStats = [
  { value: "20+ TYPHOONS", sub: "Annually" },
  { value: "72 HRS", sub: "Critical Window" },
  { value: "PROTOTYPE", sub: "Decision-Support Tool" },
];

export function About() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="about" className="relative py-20 lg:py-28 overflow-hidden">
      {/* Background */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          background:
            "radial-gradient(ellipse 70% 60% at 80% 30%, oklch(0.62 0.25 25 / 0.08) 0%, transparent 70%)",
        }}
      />

      <div ref={ref} className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
        {/* Header + Mission */}
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-16"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.65 }}
        >
          {/* Left: Mission text */}
          <div className="space-y-5">
            <div className="font-mono text-xs uppercase tracking-widest text-primary">
              About the Project
            </div>
            <h2 className="font-display font-bold text-5xl lg:text-6xl uppercase tracking-tight leading-none">
              Designed for{" "}
              <span className="text-primary">Philippine</span>{" "}
              Disaster Response
            </h2>
            <div className="space-y-4 text-muted-foreground leading-relaxed">
              <p>
                The Philippines faces over 20 typhoons per year, with catastrophic
                flood events like Ondoy (2009), Yolanda (2013), and Ulysses (2020)
                regularly isolating communities and crippling road networks across
                NCR and surrounding provinces.
              </p>
              <p>
                The first 72 hours after a major flood event are critical for life
                safety. Yet disaster responders — NDRRMC, DPWH, and local DRRMO
                offices — often lack reliable, real-time data on which roads are
                passable before dispatching rescue convoys.
              </p>
              <p>
                The UAV Flood Assessment system addresses this gap by providing <strong>a research prototype for</strong> automated,
                UAV-based road passability assessment. This capstone project demonstrates
                proof-of-concept using deep learning trained on US hurricane datasets,
                with intended deployment for Philippine disaster response after validation
                on local flood imagery.
              </p>
            </div>
          </div>

          {/* Right: Stats 2x2 */}
          <div className="grid grid-cols-2 gap-4">
            {stats.map((stat, idx) => (
              <motion.div
                key={stat.label}
                className="rounded-lg border border-white/8 bg-card p-5 space-y-1"
                initial={{ opacity: 0, scale: 0.96 }}
                animate={inView ? { opacity: 1, scale: 1 } : {}}
                transition={{ duration: 0.45, delay: 0.15 + idx * 0.08 }}
              >
                <div className="font-display font-bold text-4xl text-primary tracking-wider">
                  {stat.value}
                </div>
                <div className="font-display uppercase tracking-wide text-sm text-foreground font-semibold">
                  {stat.label}
                </div>
                <div className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  {stat.sub}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Capstone card */}
        <motion.div
          className="rounded-xl border border-primary/25 bg-primary/5 p-6 lg:p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 items-center">
            <div className="sm:col-span-2 space-y-2">
              <div className="font-mono text-xs uppercase tracking-widest text-primary">
                Academic Context
              </div>
              <h3 className="font-display font-bold text-2xl uppercase tracking-wide">
                PLM Electronics Engineering Capstone
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Bachelor of Science in Electronics Engineering (BSEcE) — Pamantasan
                ng Lungsod ng Maynila. This research explores the intersection of
                UAV technology, deep learning, and Philippine disaster preparedness.
              </p>
            </div>
            <div className="flex flex-col gap-2 font-mono text-sm">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                <span className="text-muted-foreground text-xs uppercase tracking-wider">
                  PLM BSECE Capstone 2025
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                <span className="text-muted-foreground text-xs uppercase tracking-wider">
                  Deep Learning / CNN
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                <span className="text-muted-foreground text-xs uppercase tracking-wider">
                  Disaster Response Research
                </span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stakeholders */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="text-center space-y-1">
            <div className="font-mono text-xs uppercase tracking-widest text-primary">
              Target Stakeholders
            </div>
            <h3 className="font-display font-bold text-3xl uppercase tracking-tight">
              Command Beneficiaries
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {stakeholders.map((s, idx) => (
              <motion.div
                key={s.abbr}
                className="rounded-lg border bg-card p-5 space-y-3"
                style={{ borderColor: `${s.color}25` }}
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.4 + idx * 0.1 }}
                whileHover={{ borderColor: `${s.color}50`, y: -2 }}
              >
                <div
                  className="font-display font-bold text-2xl uppercase tracking-widest"
                  style={{ color: s.color }}
                >
                  {s.abbr}
                </div>
                <div className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  {s.name}
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {s.role}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Impact stat bar */}
        <motion.div
          className="rounded-xl border border-white/8 bg-card overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-white/8">
            {impactStats.map(({ value, sub }) => (
              <div key={value} className="px-8 py-6 text-center space-y-1">
                <div className="font-display font-bold text-2xl text-foreground tracking-wider uppercase">
                  {value}
                </div>
                <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  {sub}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
