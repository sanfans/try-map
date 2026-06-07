#!/usr/bin/env python3
"""Convert mymaps-import CSVs (Name,Location,Notes,URL) into poi/*.geojson layers.

Coordinates come from the trip's .geocode-cache.json (Location string -> [lat, lon]).
Rows whose Location is not in the cache are reported and skipped.

Usage: csv2geojson.py <mymaps-import-dir> <output-poi-dir>
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

# CSV filename -> output layer filename
LAYERS = {
    "da-visitare.csv": "da-visitare.geojson",
    "degustazioni-esperienze.csv": "degustazioni-esperienze.geojson",
    "ristoranti-bar.csv": "ristoranti-bar.geojson",
    "dove-dormire.csv": "dove-dormire.geojson",
    "terme-spa.csv": "terme-spa.geojson",
}


def feature(row, lat, lon, source):
    desc = row.get("Notes", "").strip()
    url = row.get("URL", "").strip()
    if url:
        desc += f"\n[[{url}|🔗 Link]]"
    desc += f"\n[[https://maps.google.com/?q={lat},{lon}|🧭 Naviga]]"
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "name": row["Name"].strip(),
            "description": desc,
            "address": row.get("Location", "").strip(),
            "url": url,
            "source": source,
            "added": date.today().isoformat(),
        },
    }


def lookup(cache, location):
    """Full address first; on null/miss drop leading components (the
    build-osmand-gpx.py fallback strategy, whose retries are also cached)."""
    parts = [p.strip() for p in location.split(",")]
    while parts:
        coords = cache.get(", ".join(parts))
        if coords:
            return coords
        parts = parts[1:]
    return None


def main(src_dir, out_dir):
    src, out = Path(src_dir), Path(out_dir)
    cache = json.loads((src / ".geocode-cache.json").read_text())
    out.mkdir(parents=True, exist_ok=True)
    source = src.parent.name  # e.g. 2026-06-01-italia
    missing = []

    for csv_name, geojson_name in LAYERS.items():
        features = []
        with open(src / csv_name, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                coords = lookup(cache, row.get("Location", "").strip())
                if not coords:
                    missing.append(f"{csv_name}: {row['Name']}")
                    continue
                features.append(feature(row, coords[0], coords[1], source))
        fc = {"type": "FeatureCollection", "features": features}
        (out / geojson_name).write_text(
            json.dumps(fc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"{geojson_name}: {len(features)} POIs")

    if missing:
        print("\nNOT geocoded (skipped):")
        for m in missing:
            print(f"  - {m}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
