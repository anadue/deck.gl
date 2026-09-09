# Oostende — trip origins & destinations (last 365 days)

Interactive map and trip-level CSV for the Hoppy Oostende fleet, built from PathFinder
(`event_renttrans`, `data_supplier_id` 1250634911 / `hoppy_oostende_sc`).

## What's here

| File | What it is |
|---|---|
| `oostende-trip-origins-destinations.html` | Self-contained interactive map (3.8 MB). deck.gl is inlined, so it works offline apart from the basemap tiles. Open it in a browser — no server needed, no API key. |
| `oostende_trips.csv.gz` | One row per trip, 133,395 rows (30 MB uncompressed). `gunzip` to use. |
| `scripts/` | Everything needed to rebuild both artefacts. |

## Window

Requested: last 365 days (10 Sep 2025 – 9 Sep 2026, Europe/Brussels).
The Oostende feed only carries trips from **15 Dec 2025**, so the data covers
15 Dec 2025 – 9 Sep 2026 (269 days, 133,395 trips). Every trip has both an
origin and a destination fix; no rows were dropped.

## CSV columns

`rental_id, start_epoch, end_epoch, start_local, end_local, date_local, hour_local, weekday,
start_lat, start_lon, end_lat, end_lon, distance_m, duration_s, duration_min,
start_cell_id, start_cell_lat, start_cell_lon, end_cell_id, end_cell_lat, end_cell_lon,
customer_id, vehicle_id, price_eur`

Times are local (Europe/Brussels). `*_cell_id` is the ≈250 m grid cell (`R<row>C<col>`,
lat step 0.00225°, lon step 0.00359°) that the pick-up / drop-off point falls in — the same
grid the map uses at its default cell size.

## Map features

- **Cell clusters** for trip starts (green) and ends (coral), at 150 m / 250 m / 500 m,
  optionally extruded as 3D columns. Cells are named after the nearest De Lijn stop /
  landmark within ~520 m (compass suffix when a landmark covers several cells).
- **Origin → destination flows** aggregated cell→cell, with a minimum-trips threshold.
- **Individual trip origins / destinations** as point layers.
- **Filters**: date range (+ presets), hour-of-day range (+ morning/midday/evening/night),
  day of week, max duration, max distance, cell size, flow threshold.
- **Start / end cell filters**: click a green cell to keep only trips starting there, a coral
  cell to keep only trips ending there, or a flow arc to lock both ends. Table rows do the same.
- **KPIs recomputed live** for the selection: trips, share, active days, trips/day, start & end
  cells, avg distance, avg duration, total distance, CO₂ saved
  (PathFinder metric `(floor(Σdistance/1000)/1.6)×0.215`).
- **Charts**: trips per day, trips by hour, top start cells / end cells / flows.
- **Basemap**: keyless OpenStreetMap raster tiles, in three looks — dark, muted and standard.
  The dark look is the same OSM tiles desaturated and tinted in the shader by deck.gl's
  `BitmapLayer` (`desaturate` + `tintColor`), so no keyed dark-tile provider is involved.
- **Export**: "Download selection as CSV" writes the currently filtered trips.

## Rebuilding

1. Run the extraction SQL through the PathFinder MCP in 20,000-trip batches (each batch packs
   500 trips per row via `string_agg` to stay under the 500-row cap) and save the JSON results.
2. `python3 scripts/assemble.py` — parses those results into `oostende_trips.csv`.
3. `python3 scripts/build_payload.py` — columnar int32 arrays, delta-encoded timestamps,
   gzip + base64 (4.4 MB → 1.8 MB).
4. `python3 scripts/assemble_html.py` — injects payload, landmarks, deck.gl and the Hoppy /
   Anadue logos into `scripts/template.html`.
5. `node scripts/verify.js` — headless Chromium render check (KPIs, filters, cell clicks,
   console errors).

`scripts/landmarks.json` is 90 De Lijn stops around Oostende, Mariakerke and Bredene
(via the FlexMapSuper MCP), used only to give cells readable names.
