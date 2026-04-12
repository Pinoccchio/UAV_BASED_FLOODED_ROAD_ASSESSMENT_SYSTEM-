import { cn } from "@/lib/utils";
import { Waves } from "lucide-react";

const navLinks = [
  { label: "System", href: "#system" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Technology", href: "#technology" },
  { label: "About", href: "#about" },
];

const techStack = [
  "Next.js • React • TypeScript",
  "PyTorch • ONNX Runtime",
  "Tailwind CSS • Leaflet Maps",
];

export function Footer() {
  return (
    <footer className="border-t border-white/8 bg-background">
      {/* Main footer grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 lg:gap-16">
          {/* Col 1: Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Waves className="w-7 h-7" style={{ color: "oklch(0.72 0.22 200)" }} strokeWidth={2} />
              <span className="font-display font-semibold text-xl">
                UAV Flood Assessment
              </span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed max-w-xs">
              UAV-based flooded road assessment system using deep learning for
              real-time passability classification during disaster response
              operations in the Philippines.
            </p>
            <div className="font-mono text-xs text-muted-foreground/60 uppercase tracking-wider pt-2">
              <span className="text-primary/70">▶</span> BSECE Capstone 2025
            </div>
          </div>

          {/* Col 2: Navigation */}
          <div className="space-y-4">
            <h4 className="font-display uppercase tracking-widest text-sm text-foreground font-semibold">
              Navigation
            </h4>
            <ul className="space-y-2.5">
              {navLinks.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-primary transition-colors uppercase tracking-wider font-display"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
              <li>
                <a
                  href="#demo"
                  className="text-sm text-muted-foreground hover:text-primary transition-colors uppercase tracking-wider font-display"
                >
                  Demo
                </a>
              </li>
            </ul>
          </div>

          {/* Col 3: Tech Stack */}
          <div className="space-y-4">
            <h4 className="font-medium text-sm text-foreground">
              Built with
            </h4>
            <div className="text-sm text-muted-foreground space-y-1">
              {techStack.map((tech) => (
                <div key={tech}>{tech}</div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-mono text-muted-foreground/60 uppercase tracking-wider">
            <span>
              © 2025 PLM Electronics Engineering. All rights reserved.
            </span>
            <span className="text-primary/50">
              Post-Disaster Response Research
            </span>
            <span>BSECE Capstone 2025</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
