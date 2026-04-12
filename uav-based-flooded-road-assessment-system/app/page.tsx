import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Hero } from "@/components/sections/Hero";
import { Features } from "@/components/sections/Features";
import { HowItWorks } from "@/components/sections/HowItWorks";
import { AssessmentDemo } from "@/components/sections/AssessmentDemo";
import { Technology } from "@/components/sections/Technology";
import { About } from "@/components/sections/About";

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <AssessmentDemo />
        <Technology />
        <About />
      </main>
      <Footer />
    </>
  );
}
