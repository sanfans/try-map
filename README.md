# try-map — personal map database

Source of truth for my personal map: POIs (one GeoJSON file per category) + GPX tracks.
Rendered by [uMap](https://umap.openstreetmap.fr/) via **remote data layers** pointing at the raw URLs of these files. Edited locally (by hand, by Claude, or by future CLI tooling), then `git push` → the map refreshes itself.

## Structure

```
poi/
  da-visitare.geojson             # 🏛️ luoghi/città/natura
  degustazioni-esperienze.geojson # 🍷 caseifici, prosciutto, acetaie, cantine, corsi
  ristoranti-bar.geojson          # 🍝 ristoranti, osterie, aperitivi
  dove-dormire.geojson            # 🛏️ alloggi
  terme-spa.geojson               # 🧖 terme / spa
tracks/                           # GPX, one file = one route = one uMap layer
scripts/
  csv2geojson.py                  # converts trips/<trip>/mymaps-import CSVs → poi/
```

One file = one category = one uMap layer. New category = new file + new remote layer.

## POI schema

Each file is a GeoJSON `FeatureCollection` of `Point` features:

```json
{
  "type": "Feature",
  "geometry": { "type": "Point", "coordinates": [10.3265, 44.8050] },
  "properties": {
    "name": "Teatro Farnese (Pilotta)",
    "description": "Consigliato da Andrea e Matilde. …\n[[https://…|🔗 Link]]\n[[https://maps.google.com/?q=44.8050,10.3265|🧭 Naviga]]",
    "address": "Piazza della Pilotta 15, 43121 Parma PR, Italy",
    "url": "https://…",
    "source": "2026-06-01-italia",
    "added": "2026-06-07"
  }
}
```

Rules:
- **GeoJSON coordinates are `[lon, lat]`** — reversed vs. the usual lat,lon. The classic footgun.
- `description` carries the notes plus `[[url|label]]` links (uMap renders these in the default
  popup — no popup template needed): an optional 🔗 Link and always a 🧭 Naviga link
  (Google Maps, normal lat,lon order) for one-tap navigation on the phone.
- `address`, `source` (which trip/list it came from), `added` are for local grep/filtering; uMap ignores them.

## uMap layer setup (once per category)

In the map editor → *Manage layers* → *Add a layer*:

1. **Name:** the category (e.g. Ristoranti & bar)
2. **Remote data:**
   - URL: `https://raw.githubusercontent.com/sanfans/try-map/main/poi/ristoranti-bar.geojson`
   - Format: `geojson`
   - ✅ *Proxy request* (sidesteps CORS), cache duration: 5 min
3. **Shape properties:** layer color — da-visitare blu · degustazioni viola · ristoranti rosso · dormire verde · terme teal

For GPX tracks: same, but URL points at the `.gpx` file and Format = `gpx`.

## Workflow

1. Edit/add features (ask Claude, or edit the JSON directly)
2. `git commit && git push`
3. Map picks it up within the proxy cache TTL (~5 min); hard-refresh to force it
