export type SegmentStatus = "passable" | "limited" | "impassable";

export interface RoadSegmentFeature {
  type: "Feature";
  id: string;
  geometry: {
    type: "LineString";
    coordinates: [number, number][]; // [lng, lat]
  };
  properties: {
    status: SegmentStatus;
    name: string;
  };
}

export const NCR_ROAD_SEGMENTS: RoadSegmentFeature[] = [
  // ── PASSABLE (green) ──────────────────────────────────────────────
  {
    type: "Feature",
    id: "radial-road",
    geometry: {
      type: "LineString",
      coordinates: [
        [120.982, 14.598],
        [120.983, 14.599],
        [120.984, 14.601],
      ],
    },
    properties: { status: "passable", name: "Radial Road" },
  },
  {
    type: "Feature",
    id: "espana-blvd",
    geometry: {
      type: "LineString",
      coordinates: [
        [120.987, 14.603],
        [120.988, 14.604],
        [120.989, 14.605],
        [120.990, 14.606],
      ],
    },
    properties: { status: "passable", name: "España Blvd" },
  },
  {
    type: "Feature",
    id: "c3-road",
    geometry: {
      type: "LineString",
      coordinates: [
        [120.977, 14.607],
        [120.978, 14.608],
        [120.979, 14.609],
        [120.980, 14.610],
      ],
    },
    properties: { status: "passable", name: "C3 Road" },
  },

  // ── LIMITED PASSABILITY (yellow) ──────────────────────────────────
  {
    type: "Feature",
    id: "rizal-ave",
    geometry: {
      type: "LineString",
      coordinates: [
        [120.984, 14.596],
        [120.985, 14.597],
        [120.986, 14.598],
        [120.986, 14.600],
      ],
    },
    properties: { status: "limited", name: "Rizal Avenue" },
  },
  {
    type: "Feature",
    id: "claro-recto",
    geometry: {
      type: "LineString",
      coordinates: [
        [120.979, 14.599],
        [120.980, 14.600],
        [120.981, 14.601],
        [120.982, 14.602],
      ],
    },
    properties: { status: "limited", name: "Claro M. Recto Ave" },
  },

  // ── IMPASSABLE (red) ──────────────────────────────────────────────
  {
    type: "Feature",
    id: "bambang-st",
    geometry: {
      type: "LineString",
      coordinates: [
        [120.986, 14.594],
        [120.987, 14.595],
        [120.988, 14.596],
        [120.988, 14.597],
      ],
    },
    properties: { status: "impassable", name: "Bambang Street" },
  },
  {
    type: "Feature",
    id: "navotas-road",
    geometry: {
      type: "LineString",
      coordinates: [
        [120.975, 14.592],
        [120.976, 14.593],
        [120.977, 14.594],
        [120.978, 14.595],
      ],
    },
    properties: { status: "impassable", name: "Navotas Area Road" },
  },
];

export const STATUS_COLORS: Record<SegmentStatus, string> = {
  passable: "#4ade80",   // green
  limited: "#facc15",    // yellow
  impassable: "#f87171", // red
};

export const STATUS_WEIGHTS: Record<SegmentStatus, number> = {
  passable: 5,
  limited: 5,
  impassable: 5,
};
