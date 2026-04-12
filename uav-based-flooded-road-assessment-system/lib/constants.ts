/**
 * Shared constants for classification system
 * Keep in sync with Python backend (ml_backend/api/services/inference_service.py)
 */

export const CLASSIFICATION_LEVELS = {
  PASSABLE: 'passable',
  LIMITED: 'limited_passability',
  IMPASSABLE: 'impassable',
} as const;

export const CLASSIFICATION_LABELS = {
  [CLASSIFICATION_LEVELS.PASSABLE]: 'Passable',
  [CLASSIFICATION_LEVELS.LIMITED]: 'Limited Passability',
  [CLASSIFICATION_LEVELS.IMPASSABLE]: 'Impassable',
} as const;

export const CLASSIFICATION_SHORT_LABELS = {
  [CLASSIFICATION_LEVELS.PASSABLE]: 'Passable',
  [CLASSIFICATION_LEVELS.LIMITED]: 'Limited',
  [CLASSIFICATION_LEVELS.IMPASSABLE]: 'Impassable',
} as const;

export const VEHICLE_TYPES = {
  CIVILIAN_SEDAN: 'civilian_sedan',
  HIGH_CLEARANCE_SUV: 'high_clearance_suv',
  HEAVY_VEHICLE: 'heavy_vehicle',
  EMERGENCY_VEHICLE: 'emergency_vehicle',
} as const;

export type ClassificationLevel = typeof CLASSIFICATION_LEVELS[keyof typeof CLASSIFICATION_LEVELS];
export type VehicleType = typeof VEHICLE_TYPES[keyof typeof VEHICLE_TYPES];
