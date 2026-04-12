import type { Metadata, Viewport } from "next";
import { Barlow_Condensed, Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const barlowCondensed = Barlow_Condensed({
  variable: "--font-barlow",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  style: ["normal", "italic"],
  display: "swap",
});

const plusJakartaSans = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "UAV Flood Assessment — Real-time Flood Road Monitoring",
  description:
    "UAV-based system for real-time flooded road passability assessment using deep learning (ResNet/EfficientNet/MobileNet). Classifies roads into 3 passability levels for disaster response in the Philippines.",
  keywords: [
    "UAV",
    "flood assessment",
    "road passability",
    "Philippines",
    "disaster response",
    "CNN",
    "ResNet",
    "EfficientNet",
    "MobileNet",
    "deep learning",
    "NDRRMC",
    "flood mapping",
    "drone",
    "computer vision",
    "capstone",
  ],
  authors: [{ name: "PLM Electronics Engineering — BSEcE Capstone 2025" }],
};

export const viewport: Viewport = {
  themeColor: "#0a0f1a",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body
        className={`${barlowCondensed.variable} ${plusJakartaSans.variable} ${jetbrainsMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
      </body>
    </html>
  );
}
