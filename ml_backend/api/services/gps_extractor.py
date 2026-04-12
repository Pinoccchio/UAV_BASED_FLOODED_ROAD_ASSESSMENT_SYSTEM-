"""
GPS Metadata Extractor for UAV Images.

Extracts EXIF GPS data from uploaded images to demonstrate GPS-tagging capability.
Used for prototype demonstration - shows technical capability with US training data
while maintaining Philippine deployment context in frontend map visualization.
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io
from typing import Dict, Optional, Tuple
from datetime import datetime


class GPSExtractor:
    """Extract GPS and camera metadata from UAV images."""

    @staticmethod
    def dms_to_decimal(degrees: float, minutes: float, seconds: float, ref: str) -> float:
        """
        Convert GPS coordinates from DMS (Degrees, Minutes, Seconds) to decimal format.

        Args:
            degrees: Degrees component
            minutes: Minutes component
            seconds: Seconds component
            ref: Reference (N/S for latitude, E/W for longitude)

        Returns:
            Decimal coordinate
        """
        decimal = degrees + minutes / 60 + seconds / 3600

        # Make negative for South/West
        if ref in ['S', 'W']:
            decimal = -decimal

        return decimal

    @staticmethod
    def extract_gps_data(image_bytes: bytes) -> Dict:
        """
        Extract GPS metadata from image EXIF data.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Dictionary with GPS metadata or None if not found

        Example return structure:
        {
            "has_gps": true,
            "latitude": 29.942820,
            "longitude": -85.409068,
            "altitude": 55.172,
            "latitude_ref": "N",
            "longitude_ref": "W",
            "latitude_dms": "29°56'34.15\"N",
            "longitude_dms": "85°24'32.64\"W",
            "timestamp": "2018-10-15 14:32:07",
            "camera_make": "DJI",
            "camera_model": "FC6310",
            "location_note": "Training data from Hurricane Michael, Florida, USA"
        }
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            exif = image.getexif()

            if not exif:
                return GPSExtractor._no_gps_response()

            # Extract GPS info
            gps_info = {}
            for tag_id in exif:
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'GPSInfo':
                    gps_data = exif.get_ifd(tag_id)
                    for gps_tag_id in gps_data:
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[gps_tag] = gps_data.get(gps_tag_id)

            # If no GPS data found
            if not gps_info:
                return GPSExtractor._no_gps_response()

            # Parse GPS coordinates
            result = GPSExtractor._parse_gps_info(gps_info, exif)

            return result

        except Exception as e:
            print(f"GPS extraction error: {str(e)}")
            return GPSExtractor._no_gps_response()

    @staticmethod
    def _parse_gps_info(gps_info: Dict, exif) -> Dict:
        """Parse GPS info into structured format."""
        result = {"has_gps": True}

        print(f"DEBUG: Parsing GPS info: {list(gps_info.keys())}")

        try:
            # Extract latitude
            if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
                lat_dms = gps_info['GPSLatitude']
                lat_ref = gps_info['GPSLatitudeRef']

                # Handle IFDRational objects - convert to float
                lat_deg = float(lat_dms[0]) if hasattr(lat_dms[0], 'numerator') else lat_dms[0]
                lat_min = float(lat_dms[1]) if hasattr(lat_dms[1], 'numerator') else lat_dms[1]
                lat_sec = float(lat_dms[2]) if hasattr(lat_dms[2], 'numerator') else lat_dms[2]

                # Convert to decimal
                lat_decimal = GPSExtractor.dms_to_decimal(
                    lat_deg,
                    lat_min,
                    lat_sec,
                    lat_ref
                )

                result['latitude'] = round(lat_decimal, 6)
                result['latitude_ref'] = lat_ref
                result['latitude_dms'] = f"{int(lat_deg)}°{int(lat_min)}'{lat_sec:.2f}\"{lat_ref}"

            # Extract longitude
            if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
                lon_dms = gps_info['GPSLongitude']
                lon_ref = gps_info['GPSLongitudeRef']

                # Handle IFDRational objects - convert to float
                lon_deg = float(lon_dms[0]) if hasattr(lon_dms[0], 'numerator') else lon_dms[0]
                lon_min = float(lon_dms[1]) if hasattr(lon_dms[1], 'numerator') else lon_dms[1]
                lon_sec = float(lon_dms[2]) if hasattr(lon_dms[2], 'numerator') else lon_dms[2]

                # Convert to decimal
                lon_decimal = GPSExtractor.dms_to_decimal(
                    lon_deg,
                    lon_min,
                    lon_sec,
                    lon_ref
                )

                result['longitude'] = round(lon_decimal, 6)
                result['longitude_ref'] = lon_ref
                result['longitude_dms'] = f"{int(lon_deg)}°{int(lon_min)}'{lon_sec:.2f}\"{lon_ref}"

            # Extract altitude
            if 'GPSAltitude' in gps_info:
                alt_val = gps_info['GPSAltitude']
                # Handle IFDRational
                alt_float = float(alt_val) if hasattr(alt_val, 'numerator') else alt_val
                result['altitude'] = round(alt_float, 2)
        except Exception as e:
            print(f"ERROR parsing GPS coordinates: {e}")
            import traceback
            traceback.print_exc()
            # Return partial result if some fields succeeded

        print(f"DEBUG: Parsed GPS result: latitude={result.get('latitude')}, longitude={result.get('longitude')}")

        # If latitude/longitude are still missing, return no GPS
        if 'latitude' not in result or 'longitude' not in result:
            print("WARNING: GPS coordinates could not be parsed")
            return GPSExtractor._no_gps_response()

        # Extract camera info from main EXIF
        if exif:
            # Camera make
            make = exif.get(271)  # Make tag
            if make:
                result['camera_make'] = make

            # Camera model
            model = exif.get(272)  # Model tag
            if model:
                result['camera_model'] = model

            # Timestamp
            timestamp = exif.get(306)  # DateTime tag
            if timestamp:
                try:
                    # Parse timestamp (format: "2018:10:15 14:32:07")
                    dt = datetime.strptime(timestamp, "%Y:%m:%d %H:%M:%S")
                    result['timestamp'] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    result['timestamp'] = timestamp

        # Add location note based on coordinates
        result['location_note'] = GPSExtractor._get_location_note(
            result.get('latitude'),
            result.get('longitude')
        )

        return result

    @staticmethod
    def _get_location_note(lat: Optional[float], lon: Optional[float]) -> str:
        """
        Determine location note based on coordinates.

        Training datasets are from:
        - RescueNet: Hurricane Michael, Florida (~29.94°N, -85.41°W)
        - FloodNet: Hurricane Harvey, Texas (~29.62°N, -95.72°W)
        """
        if lat is None or lon is None:
            return "Unknown location"

        # Florida (RescueNet)
        if 29.5 <= lat <= 30.5 and -86 <= lon <= -85:
            return "Training data from Hurricane Michael, Florida, USA (RescueNet dataset)"

        # Texas (FloodNet)
        if 29.0 <= lat <= 30.0 and -96 <= lon <= -95:
            return "Training data from Hurricane Harvey, Texas, USA (FloodNet dataset)"

        # Philippine coordinates (future deployment)
        if 14.0 <= lat <= 15.0 and 120.0 <= lon <= 121.5:
            return "Philippine flood imagery (deployment data)"

        # Unknown
        return f"Location: {lat:.4f}°, {lon:.4f}°"

    @staticmethod
    def _no_gps_response() -> Dict:
        """Return response when no GPS data is found."""
        return {
            "has_gps": False,
            "location_note": "No GPS data found in image EXIF. Image may not be from GPS-enabled UAV."
        }


if __name__ == "__main__":
    """Test GPS extraction on sample dataset images."""
    from pathlib import Path

    print("="*60)
    print("GPS Extractor Test")
    print("="*60)

    # Test with RescueNet image
    test_image_path = Path(__file__).parent.parent.parent.parent / "datasets" / "RescueNet" / "test" / "test-org-img" / "13363.jpg"

    if test_image_path.exists():
        print(f"\nTesting with: {test_image_path.name}")

        with open(test_image_path, 'rb') as f:
            image_bytes = f.read()

        gps_data = GPSExtractor.extract_gps_data(image_bytes)

        print("\nExtracted GPS Data:")
        print("-" * 60)
        for key, value in gps_data.items():
            print(f"  {key:20s}: {value}")

        print("\n[OK] GPS extraction test complete!")
    else:
        print(f"\nTest image not found: {test_image_path}")
        print("Please ensure RescueNet dataset is downloaded.")

    print("="*60)
