"use client";

import { useEffect, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";
import {
  NCR_ROAD_SEGMENTS,
  STATUS_COLORS,
  STATUS_WEIGHTS,
  type SegmentStatus,
} from "./floodMapData";

type SegmentId = "passable" | "limited" | "impassable";

interface FloodMapProps {
  variant: "hero" | "demo";
  activeSegmentId?: SegmentId;
  onSegmentClick?: (id: SegmentId) => void;
  center?: [number, number];     // Dynamic center [lat, lng]
  zoom?: number;                 // Dynamic zoom level
  showRealLocation?: boolean;    // Flag for real GPS data
  realLocationClass?: SegmentId; // Classification for real location (for color)
}

// Map center: Tondo/Navotas area, Manila
const MAP_CENTER: [number, number] = [14.5995, 120.9842];

const TILE_DARK = {
  url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
  attr: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
  maxZoom: 20,
};

const TILE_SATELLITE = {
  url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  attr: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
  maxZoom: 18,
};

export function FloodMap({
  variant,
  activeSegmentId,
  onSegmentClick,
  center,
  zoom,
  showRealLocation = false,
  realLocationClass
}: FloodMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<import("leaflet").Map | null>(null);
  const tileRef = useRef<import("leaflet").TileLayer | null>(null);
  const geoLayerRef = useRef<import("leaflet").GeoJSON | null>(null);
  const [isSatellite, setIsSatellite] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const activeSegmentIdRef = useRef(activeSegmentId);

  // Keep ref in sync so GeoJSON style function stays current without re-init
  useEffect(() => {
    activeSegmentIdRef.current = activeSegmentId;
    // Re-style existing GeoJSON layer when active segment changes
    if (geoLayerRef.current) {
      geoLayerRef.current.setStyle((feature) => {
        if (!feature) return {};
        const status = feature.properties?.status as SegmentStatus;
        const segId = feature.id as string;
        const isActive = segId === activeSegmentIdRef.current ||
          status === activeSegmentIdRef.current;
        return {
          color: STATUS_COLORS[status],
          weight: isActive ? STATUS_WEIGHTS[status] + 3 : STATUS_WEIGHTS[status],
          opacity: isActive ? 1 : 0.65,
        };
      });
    }
  }, [activeSegmentId]);

  // Initialize Leaflet map
  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted || !containerRef.current || mapRef.current) return;

    // Dynamic import to avoid SSR issues
    import("leaflet").then((L) => {
      if (!containerRef.current || mapRef.current) return;

      // Use dynamic center/zoom if provided, otherwise use defaults
      const mapCenter = center || MAP_CENTER;
      const mapZoom = zoom ?? (variant === "hero" ? 14 : 15);

      const map = L.map(containerRef.current, {
        center: mapCenter,
        zoom: mapZoom,
        zoomControl: false,
        scrollWheelZoom: true,
        attributionControl: false,
      });

      // Add zoom control to bottom-right
      L.control.zoom({ position: "bottomright" }).addTo(map);

      // Add attribution control (minimal, bottom-left)
      L.control.attribution({ position: "bottomleft", prefix: false }).addTo(map);

      // Add dark tile layer
      const tileLayer = L.tileLayer(TILE_DARK.url, {
        attribution: TILE_DARK.attr,
        maxZoom: TILE_DARK.maxZoom,
      }).addTo(map);

      tileRef.current = tileLayer;

      // Build GeoJSON layer with color-coded polylines
      const geoJson = L.geoJSON(
        { type: "FeatureCollection", features: NCR_ROAD_SEGMENTS } as GeoJSON.FeatureCollection,
        {
          style: (feature) => {
            if (!feature) return {};
            const status = feature.properties?.status as SegmentStatus;
            const segId = feature.id as string;
            const isActive = segId === activeSegmentIdRef.current ||
              status === activeSegmentIdRef.current;
            return {
              color: STATUS_COLORS[status],
              weight: isActive ? STATUS_WEIGHTS[status] + 3 : STATUS_WEIGHTS[status],
              opacity: isActive ? 1 : 0.65,
            };
          },
          onEachFeature: (feature, layer) => {
            if (variant !== "demo") return;
            layer.on("click", () => {
              const status = feature.properties?.status as SegmentId;
              onSegmentClick?.(status);
            });
            // Cursor pointer on hover
            layer.on("mouseover", () => {
              const s = feature.properties?.status as SegmentStatus;
              (layer as import("leaflet").Polyline).setStyle({ weight: STATUS_WEIGHTS[s] + 5, opacity: 1 });
            });
            layer.on("mouseout", () => {
              geoJson.resetStyle(layer);
            });
            // Tooltip with road name
            layer.bindTooltip(
              `<span style="font-family:monospace;font-size:11px;color:#fff;background:transparent">${feature.properties?.name}</span>`,
              { sticky: true, className: "flood-map-tooltip" }
            );
          },
        }
      ).addTo(map);

      geoLayerRef.current = geoJson;
      mapRef.current = map;

      // Fix grey tiles on initial render
      setTimeout(() => map.invalidateSize(), 150);
    });

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        tileRef.current = null;
        geoLayerRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isMounted]);

  // Toggle satellite / dark tile layer
  const handleSatelliteToggle = () => {
    if (!mapRef.current || !tileRef.current) return;
    import("leaflet").then((L) => {
      if (!mapRef.current || !tileRef.current) return;
      mapRef.current.removeLayer(tileRef.current);
      const next = isSatellite ? TILE_DARK : TILE_SATELLITE;
      tileRef.current = L.tileLayer(next.url, {
        attribution: next.attr,
        maxZoom: next.maxZoom,
      });
      // Insert tile layer below GeoJSON
      tileRef.current.addTo(mapRef.current);
      if (geoLayerRef.current) {
        geoLayerRef.current.bringToFront();
      }
      setIsSatellite((prev) => !prev);
    });
  };

  // Pan/zoom map when center prop changes (e.g., when GPS data arrives)
  useEffect(() => {
    if (!mapRef.current || !center) return;

    import("leaflet").then((L) => {
      if (!mapRef.current || !center) return;

      // Smooth fly to new location
      mapRef.current.flyTo(center, zoom ?? 15, {
        duration: 1.5,
        easeLinearity: 0.25,
      });

      // Add a coverage area circle at the GPS location if it's real data
      if (showRealLocation && realLocationClass) {
        // Remove existing real location layers first
        mapRef.current.eachLayer((layer) => {
          if ((layer instanceof L.Circle || layer instanceof L.CircleMarker) && (layer as any)._realLocation) {
            mapRef.current?.removeLayer(layer);
          }
        });

        // Get color based on classification
        const segmentColor = STATUS_COLORS[realLocationClass as SegmentStatus];

        // Create a coverage area circle (approximate UAV image footprint)
        // At 40-50m altitude, camera covers ~80-100m diameter
        const coverageCircle = L.circle(center, {
          radius: 80,  // 80 meters radius (160m diameter coverage area)
          color: segmentColor,
          fillColor: segmentColor,
          fillOpacity: 0.25,
          weight: 3,
          opacity: 0.8,
        });

        // Mark as real location layer for cleanup
        (coverageCircle as any)._realLocation = true;

        coverageCircle.addTo(mapRef.current);

        // Add center point marker
        const centerMarker = L.circleMarker(center, {
          radius: 6,
          color: '#ffffff',
          fillColor: segmentColor,
          fillOpacity: 1,
          weight: 2,
        });

        (centerMarker as any)._realLocation = true;
        centerMarker.addTo(mapRef.current);

        // Add popup showing classification and coverage info
        const popupContent = `
          <div style="font-family: monospace; font-size: 11px; color: #000;">
            <strong style="text-transform: uppercase; color: ${segmentColor};">${realLocationClass}</strong><br/>
            GPS: ${center[0].toFixed(6)}°, ${center[1].toFixed(6)}°<br/>
            <em style="font-size: 10px;">Coverage: ~160m diameter (UAV image footprint)</em><br/>
            <em style="font-size: 10px;">AI classification from uploaded aerial image</em>
          </div>
        `;

        coverageCircle.bindPopup(popupContent);
        centerMarker.bindPopup(popupContent);
      }
    });
  }, [center, zoom, showRealLocation, realLocationClass]);

  return (
    <div className="relative overflow-hidden w-full h-full">
      {/* Leaflet map container */}
      <div
        ref={containerRef}
        style={{ width: "100%", height: "100%" }}
        className="flood-map-container"
      />

      {/* Satellite toggle button - enhanced touch target */}
      <button
        onClick={handleSatelliteToggle}
        className="absolute top-4 right-4 px-4 py-3 min-h-[44px] bg-card border border-border rounded-md text-sm font-medium shadow-sm hover:shadow-md transition-all hover:bg-card/80 z-[1000] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        aria-label={isSatellite ? "Switch to map view" : "Switch to satellite view"}
      >
        {isSatellite ? "Map view" : "Satellite view"}
      </button>

      {/* Loading overlay — shown before isMounted */}
      {!isMounted && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "oklch(0.08 0.012 245)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 600,
          }}
        >
          <span
            style={{
              fontFamily: "monospace",
              fontSize: 11,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: "oklch(0.72 0.22 200 / 0.6)",
            }}
          >
            Loading map...
          </span>
        </div>
      )}
    </div>
  );
}
