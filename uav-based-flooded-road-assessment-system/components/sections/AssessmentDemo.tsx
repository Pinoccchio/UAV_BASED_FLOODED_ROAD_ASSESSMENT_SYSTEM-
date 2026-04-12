"use client";

import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { FloodMap } from "@/components/map/FloodMap";
import { Check, X, AlertTriangle, Download } from "lucide-react";

/* ============================================================
   TYPE DEFINITIONS
   ============================================================ */

type SegmentId = "passable" | "limited" | "impassable";

interface VehicleRow {
  type: string;
  icon: string;
  allowed: boolean;
}

interface SegmentData {
  id: SegmentId;
  label: string;
  badge: "passable" | "limited" | "impassable";
  color: string;
  confidence: number;
  vehicles: VehicleRow[];
  lat: string;
  lng: string;
}

/* ============================================================
   DATA
   ============================================================ */

const segments: SegmentData[] = [
  {
    id: "passable",
    label: "Passable",
    badge: "passable",
    color: "var(--status-passable)",
    confidence: 94.2,
    vehicles: [
      { type: "Civilian sedan", icon: "🚗", allowed: true },
      { type: "High-clearance SUV", icon: "🚙", allowed: true },
      { type: "Heavy/Bus", icon: "🚌", allowed: true },
      { type: "Emergency vehicle", icon: "🚑", allowed: true },
    ],
    lat: "14.6010° N",
    lng: "120.9822° E",
  },
  {
    id: "limited",
    label: "Limited passability",
    badge: "limited",
    color: "var(--status-limited)",
    confidence: 89.6,
    vehicles: [
      { type: "Civilian sedan", icon: "🚗", allowed: false },
      { type: "High-clearance SUV", icon: "🚙", allowed: true },
      { type: "Heavy/Bus", icon: "🚌", allowed: true },
      { type: "Emergency vehicle", icon: "🚑", allowed: true },
    ],
    lat: "14.5995° N",
    lng: "120.9842° E",
  },
  {
    id: "impassable",
    label: "Impassable",
    badge: "impassable",
    color: "var(--status-impassable)",
    confidence: 96.1,
    vehicles: [
      { type: "Civilian sedan", icon: "🚗", allowed: false },
      { type: "High-clearance SUV", icon: "🚙", allowed: false },
      { type: "Heavy/Bus", icon: "🚌", allowed: false },
      { type: "Emergency vehicle", icon: "🚑", allowed: false },
    ],
    lat: "14.5952° N",
    lng: "120.9891° E",
  },
];

/* Sample images for quick testing */
interface SampleImage {
  id: string;
  name: string;
  description: string;
  url: string;
  expectedClass: SegmentId;
}

const sampleImages: SampleImage[] = [
  {
    id: "passable-1",
    name: "Clear Road",
    description: "Minimal water, safe passage",
    url: "/sample-images/passable-road.jpg",
    expectedClass: "passable"
  },
  {
    id: "limited-1",
    name: "Moderate Flood",
    description: "Water ~30cm, high vehicles only",
    url: "/sample-images/limited-flood.jpg",
    expectedClass: "limited"
  },
  {
    id: "impassable-1",
    name: "Severe Flood",
    description: "Deep water, road closed",
    url: "/sample-images/impassable-flood.jpg",
    expectedClass: "impassable"
  }
];

/* ============================================================
   CONFIDENCE COUNTER HOOK
   ============================================================ */

function useCountUp(target: number, active: boolean) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!active) return;
    setCount(0);
    const duration = 900;
    const start = performance.now();
    let raf: number;
    const animate = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(target * eased * 10) / 10);
      if (progress < 1) raf = requestAnimationFrame(animate);
    };
    raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, [target, active]);
  return count;
}

/* ============================================================
   MAIN COMPONENT
   ============================================================ */

export function AssessmentDemo() {
  const [activeId, setActiveId] = useState<SegmentId>("passable");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [visible, setVisible] = useState(true);
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null);
  const [predictionResult, setPredictionResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedSampleId, setSelectedSampleId] = useState<string | null>(null);

  const activeSegment = segments.find((s) => s.id === activeId)!;
  const confidence = useCountUp(
    predictionResult ? predictionResult.prediction.confidence * 100 : activeSegment.confidence,
    visible && !isAnalyzing
  );

  const exportResults = () => {
    if (!predictionResult) return;

    const exportData = {
      timestamp: new Date().toISOString(),
      system: "UAV Flood Assessment System - PLM BSEcE Capstone 2025",
      prediction: {
        class: predictionResult.prediction.class,
        confidence: predictionResult.prediction.confidence,
        confidence_level: predictionResult.prediction.confidence_level,
        probabilities: predictionResult.prediction.probabilities
      },
      vehicle_recommendations: predictionResult.vehicle_recommendations,
      image_metadata: predictionResult.image_metadata || {},
      safety_info: predictionResult.safety_info || {},
      uploaded_image: uploadedImage?.name || "sample_image"
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `flood-assessment-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImageUpload = async (file: File) => {
    setIsUploading(true);
    setIsAnalyzing(true);
    setError(null);
    setVisible(false);
    setSelectedSampleId(null); // Clear sample selection when uploading

    try {
      const imageUrl = URL.createObjectURL(file);
      setUploadedImageUrl(imageUrl);
      setUploadedImage(file);

      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('/api/predict', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Prediction failed');
      }

      const result = await response.json();

      if (!result.prediction?.class || !result.vehicle_recommendations) {
        console.error('Invalid backend response format:', result);
        throw new Error('Received invalid response from AI model. Please try again.');
      }

      setPredictionResult(result);

      const classMap: Record<string, SegmentId> = {
        'passable': 'passable',
        'limited_passability': 'limited',
        'impassable': 'impassable'
      };

      const predictedClass = result.prediction.class;
      const segmentId = classMap[predictedClass];
      setActiveId(segmentId);

    } catch (err) {
      console.error('Upload error:', err);
      setError(err instanceof Error ? err.message : 'Failed to analyze image. Please try again.');
    } finally {
      setIsUploading(false);
      setTimeout(() => {
        setIsAnalyzing(false);
        setVisible(true);
      }, 500);
    }
  };

  const handleSampleImageClick = async (sample: SampleImage) => {
    setSelectedSampleId(sample.id);
    setIsUploading(true);
    setIsAnalyzing(true);
    setError(null);
    setVisible(false);

    try {
      // Fetch the sample image
      const response = await fetch(sample.url);
      const blob = await response.blob();
      const file = new File([blob], sample.name.toLowerCase().replace(/\s+/g, '-') + '.jpg', { type: 'image/jpeg' });

      setUploadedImageUrl(sample.url);
      setUploadedImage(file);

      const formData = new FormData();
      formData.append('image', file);

      const predictResponse = await fetch('/api/predict', {
        method: 'POST',
        body: formData,
      });

      if (!predictResponse.ok) {
        const errorData = await predictResponse.json();
        throw new Error(errorData.error || 'Prediction failed');
      }

      const result = await predictResponse.json();

      if (!result.prediction?.class || !result.vehicle_recommendations) {
        console.error('Invalid backend response format:', result);
        throw new Error('Received invalid response from AI model. Please try again.');
      }

      setPredictionResult(result);

      const classMap: Record<string, SegmentId> = {
        'passable': 'passable',
        'limited_passability': 'limited',
        'impassable': 'impassable'
      };

      const predictedClass = result.prediction.class;
      const segmentId = classMap[predictedClass];
      setActiveId(segmentId);

    } catch (err) {
      console.error('Sample image error:', err);
      setError(err instanceof Error ? err.message : 'Failed to analyze sample image. Please try again.');
    } finally {
      setIsUploading(false);
      setTimeout(() => {
        setIsAnalyzing(false);
        setVisible(true);
      }, 500);
    }
  };

  const switchSegment = useCallback((id: SegmentId) => {
    if (isAnalyzing) return;
    setPredictionResult(null);
    setSelectedSampleId(null); // Clear sample selection
    setIsAnalyzing(true);
    setVisible(false);
    setTimeout(() => {
      setActiveId(id);
      setIsAnalyzing(false);
      setVisible(true);
    }, 800);
  }, [isAnalyzing]);

  return (
    <section id="demo" className="relative py-20 lg:py-28">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        {/* Header - Centered */}
        <div className="mb-12 space-y-3 text-center max-w-3xl mx-auto">
          <h2 className="font-display text-3xl lg:text-4xl font-semibold">
            Try the demo
          </h2>
          <p className="text-muted-foreground text-lg">
            Upload your own flood image or click a sample image below for instant testing.
          </p>
        </div>

        {/* Sample Images Gallery - Centered */}
        <div className="mb-8 max-w-3xl mx-auto">
          <h3 className="text-sm font-medium text-muted-foreground mb-3 text-center">
            Quick Test: Sample Images (Hurricane Michael 2018)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {sampleImages.map((sample) => (
              <button
                key={sample.id}
                onClick={() => handleSampleImageClick(sample)}
                disabled={isUploading}
                className={cn(
                  "group relative rounded-lg border transition-all overflow-hidden",
                  "hover:border-primary/50 hover:shadow-lg hover:scale-[1.02]",
                  "disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100",
                  selectedSampleId === sample.id
                    ? "border-primary/50 bg-primary/5 ring-2 ring-primary/30"
                    : "border-border bg-card"
                )}
              >
                <div className="aspect-video bg-muted/30 flex items-center justify-center">
                  <div className="text-center p-3">
                    <div className="text-3xl mb-2">
                      {sample.expectedClass === 'passable' && '✅'}
                      {sample.expectedClass === 'limited' && '⚠️'}
                      {sample.expectedClass === 'impassable' && '🚫'}
                    </div>
                    <div className="text-xs font-medium">{sample.name}</div>
                  </div>
                </div>
                <div className="p-2 border-t border-border/50 bg-card/50">
                  <p className="text-xs text-muted-foreground text-center">
                    {sample.description}
                  </p>
                </div>
                {selectedSampleId === sample.id && (
                  <div className="absolute top-2 right-2 bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
                    ✓
                  </div>
                )}
              </button>
            ))}
          </div>
          <p className="text-xs text-muted-foreground text-center mt-3">
            Sample images from RescueNet dataset (Hurricane Michael, USA 2018). Click to test AI classification.
          </p>
        </div>

        {/* Disclaimer Banner - Centered */}
        <div className="mb-8 max-w-3xl mx-auto">
          <div className="p-4 rounded-lg border border-yellow-500/30 bg-yellow-500/10">
            <div className="flex items-start gap-3">
              <span className="text-xl flex-shrink-0">⚠️</span>
              <div className="space-y-2 text-sm">
                <div className="font-semibold text-yellow-200">Prototype research system</div>
                <ul className="space-y-1 text-yellow-100/80 text-sm">
                  <li>• Trained on US hurricane data (Hurricane Michael 2018, not current conditions)</li>
                  <li>• Sample images from USA 2018, map shows Philippines NCR (demo only)</li>
                  <li>• Expected Philippine accuracy: ~65-70% (domain shift + temporal gap)</li>
                  <li>• For demonstration/research only — not for emergency deployment</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Side-panel layout: Controls (35%) + Map (65%) */}
        <div className="grid grid-cols-1 lg:grid-cols-[35%_65%] gap-6 lg:gap-8">
          {/* Left Column: Upload + Controls + Results */}
          <div className="order-2 lg:order-1 space-y-6 lg:max-h-[70vh] lg:overflow-y-auto lg:pr-2">
            {/* File Upload Section */}
            <div className="rounded-lg border border-border bg-card p-6">
              <label htmlFor="image-upload" className="block cursor-pointer" aria-label="Upload flood image for analysis">
                <div className={cn(
                  "flex flex-col items-center gap-4 p-8 border-2 border-dashed rounded-lg transition-all",
                  isUploading ? "border-primary/50 bg-primary/5" : "border-border hover:border-primary/50 hover:bg-card/50"
                )}>
                  <div className="text-4xl">{isUploading ? "⏳" : "📁"}</div>
                  <div className="text-center">
                    <p className="font-medium text-lg mb-2">
                      {isUploading ? "Analyzing image..." : "Upload flood image"}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {isUploading ? "AI classification in progress" : "Supports JPEG, PNG (max 10MB)"}
                    </p>
                  </div>
                  {uploadedImage && !isUploading && (
                    <p className="text-sm text-primary font-mono">
                      Selected: {uploadedImage.name}
                    </p>
                  )}
                </div>
              </label>
              <input
                id="image-upload"
                type="file"
                accept="image/jpeg,image/jpg,image/png"
                className="hidden"
                disabled={isUploading}
                aria-describedby="upload-help"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleImageUpload(file);
                }}
              />
              <p id="upload-help" className="sr-only">
                Upload JPEG or PNG image, maximum 10MB file size
              </p>
            </div>

            {/* Error Display */}
            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {/* Safety Warning Display */}
            {predictionResult?.safety_info?.safety_applied && (
              <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <p className="text-yellow-400 font-semibold text-sm mb-2">
                  🛡️ Safety measure applied
                </p>
                <p className="text-sm text-white/80">
                  {predictionResult.safety_info.safety_reason}
                </p>
                {predictionResult.safety_info.original_prediction && (
                  <p className="text-xs text-muted-foreground mt-2">
                    Original: {predictionResult.safety_info.original_prediction.class} ({(predictionResult.safety_info.original_prediction.confidence * 100).toFixed(1)}%)
                  </p>
                )}
              </div>
            )}

            {/* Sample scenario tabs */}
            <div className="flex gap-2">
              {segments.map((seg) => (
                <button
                  key={seg.id}
                  onClick={() => switchSegment(seg.id)}
                  disabled={isAnalyzing}
                  className={cn(
                    "flex-1 px-4 py-3 min-h-[44px] rounded-md border text-sm font-medium transition-all",
                    "disabled:opacity-60 disabled:cursor-not-allowed",
                    activeId === seg.id
                      ? "border-primary/50 bg-primary/10 text-primary"
                      : "border-border hover:border-border/80 hover:bg-card/50"
                  )}
                >
                  {seg.label}
                </button>
              ))}
            </div>

            <AnimatePresence mode="wait">
              {isAnalyzing ? (
                <motion.div
                  key="analyzing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col items-center justify-center py-16 gap-4"
                >
                  <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  <div className="text-sm text-primary">AI classification in progress...</div>
                </motion.div>
              ) : (
                <motion.div
                  key={activeId}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -12 }}
                  transition={{ duration: 0.4 }}
                  className="space-y-6"
                >
                  {/* Sample/Real Indicator */}
                  {!predictionResult ? (
                    <div className="px-4 py-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                      <div className="flex items-center gap-2">
                        <span className="text-blue-400 text-lg">ℹ️</span>
                        <div>
                          <p className="text-blue-300 font-medium text-sm">Sample scenario</p>
                          <p className="text-blue-400/80 text-xs mt-0.5">
                            Upload your own flood image above to get real AI predictions
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="px-4 py-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                      <div className="flex items-center gap-2">
                        <span className="text-green-400 text-lg">✓</span>
                        <div>
                          <p className="text-green-300 font-medium text-sm">Real AI prediction</p>
                          <p className="text-green-400/80 text-xs mt-0.5">
                            Classification by EfficientNet-B0 model (78.4% US accuracy)
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Classification & Confidence */}
                  <div className="flex items-center justify-between">
                    <Badge variant={activeSegment.badge} className="text-sm px-3 py-1.5 gap-1.5">
                      {activeSegment.badge === 'passable' && <Check size={14} />}
                      {activeSegment.badge === 'limited' && <AlertTriangle size={14} />}
                      {activeSegment.badge === 'impassable' && <X size={14} />}
                      {activeSegment.label}
                    </Badge>
                    <div className="text-right">
                      <div className="text-3xl font-semibold" style={{ color: activeSegment.color }}>
                        {confidence.toFixed(1)}%
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {predictionResult?.prediction.confidence_level || "Confidence"}
                      </div>
                    </div>
                  </div>

                  {/* Confidence bar */}
                  <div className="h-2 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      className="h-full rounded-full transition-all duration-1000"
                      style={{ backgroundColor: activeSegment.color }}
                      initial={{ width: 0 }}
                      animate={{ width: `${activeSegment.confidence}%` }}
                    />
                  </div>

                  {/* Vehicle recommendations (simplified table) */}
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium">Vehicle passability</h3>
                    <div className="border border-border rounded-lg divide-y divide-border">
                      {(predictionResult ? [
                        { type: "Civilian sedan", icon: "🚗", allowed: predictionResult.vehicle_recommendations?.civilian_sedan ?? false },
                        { type: "High-clearance SUV", icon: "🚙", allowed: predictionResult.vehicle_recommendations?.high_clearance_suv ?? false },
                        { type: "Heavy/Bus", icon: "🚌", allowed: predictionResult.vehicle_recommendations?.heavy_vehicle ?? false },
                        { type: "Emergency vehicle", icon: "🚑", allowed: predictionResult.vehicle_recommendations?.emergency_vehicle ?? false },
                      ] : activeSegment.vehicles).map((v) => (
                        <div
                          key={v.type}
                          className="flex items-center justify-between p-3"
                        >
                          <span className="flex items-center gap-2 text-sm">
                            <span className="text-lg">{v.icon}</span>
                            {v.type}
                          </span>
                          <span className={cn(
                            "flex items-center gap-1 text-sm font-medium",
                            v.allowed ? "text-[var(--status-passable)]" : "text-[var(--status-impassable)]"
                          )}>
                            {v.allowed ? (
                              <>
                                <Check size={16} /> Allowed
                              </>
                            ) : (
                              <>
                                <X size={16} /> Blocked
                              </>
                            )}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* GPS metadata (condensed) */}
                  {predictionResult?.image_metadata?.has_gps && (
                    <div className="p-3 rounded-lg bg-primary/5 border border-primary/20">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-primary">📍</span>
                        <span className="font-medium text-sm">GPS location</span>
                      </div>
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div>
                          {predictionResult.image_metadata.latitude_dms}, {predictionResult.image_metadata.longitude_dms}
                        </div>
                        {predictionResult.image_metadata.altitude && (
                          <div className="text-xs">Altitude: {predictionResult.image_metadata.altitude}m</div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Export Results Button */}
                  {predictionResult && (
                    <button
                      onClick={exportResults}
                      className={cn(
                        "w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg",
                        "bg-primary/10 hover:bg-primary/20 border border-primary/30",
                        "text-primary font-medium text-sm transition-all",
                        "hover:shadow-lg hover:scale-[1.02]"
                      )}
                    >
                      <Download size={16} />
                      Download Results (JSON)
                    </button>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Right Column: Map (sticky on desktop) */}
          <div className="order-1 lg:order-2 h-[50vh] lg:h-[70vh] border border-border rounded-lg overflow-hidden lg:sticky lg:top-24">
            <FloodMap
              variant="demo"
              activeSegmentId={activeId}
              onSegmentClick={(id) => switchSegment(id)}
              center={predictionResult?.image_metadata?.has_gps ?
                [predictionResult.image_metadata.latitude, predictionResult.image_metadata.longitude]
                : undefined
              }
              zoom={predictionResult?.image_metadata?.has_gps ? 16 : undefined}
              showRealLocation={!!predictionResult?.image_metadata?.has_gps}
              realLocationClass={predictionResult?.prediction?.class === 'limited_passability' ? 'limited' :
                                 predictionResult?.prediction?.class as SegmentId}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
