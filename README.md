
<div align="center">

# Parametric Daylight Room Study 2026

[![Code licence: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)
[![Data licence: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-green)](LICENSE-DATA)

</div>

Supporting dataset for a study of the **1/8 Window-to-Floor Ratio (WFR)** rule under climate-based daylight modelling, covering **4,320 single-side-lit residential room configurations** in Warsaw and Berlin.

Every configuration in this dataset is **exactly compliant** with the 1/8 (12.5%) WFR requirement found in the Polish *Warunki techniczne* and the German *Musterbauordnung*. The dataset records what that compliance actually delivers in terms of spatial Daylight Autonomy (sDA<sub>300/50%</sub>) and Annual Sunlight Exposure (ASE<sub>1000,250</sub>) as room geometry, façade orientation and street canyon density vary.

> **Status:** the associated manuscript is under double-anonymous peer review. Author, affiliation and citation metadata will be added to this repository once the review process concludes.

---

## Contents

```
.
├── README.md
└── study/
    ├── study.xlsx              # 4,320 simulation records (single sheet, 25 columns)
    └── da-grids/
        └── iteration_0000.png … iteration_4319.png   # per-case daylight autonomy grid renders
```

`iteration_NNNN.png` maps 1:1 onto the `Iteration_Nr` column of `study.xlsx` (0–4319, unique).

---

## Design space

The simulation sweeps six independent parameters. Glazing area is recomputed for every permutation so that the window is always exactly 12.5% of the floor area.

| Parameter | Values | Levels |
|---|---|---|
| Location (EPW) | Warsaw-Okęcie (123750), Berlin (103840) | 2 |
| Façade orientation | South 0°, West 90°, North 180°, East 270° | 4 |
| Room width | 3.0 – 7.0 m, 0.5 m steps | 9 |
| Room depth | 3.0 – 7.0 m, 1.0 m steps | 5 |
| Window head height | 1.4, 1.7, 2.0 m | 3 |
| Street aspect ratio H/W | 0.0, 0.5, 1.0, 1.5 | 4 |
| **Total** | | **4,320** |

Fixed across all cases: floor-to-ceiling height 2.7 m; sill height 0.8 m; window centred on the exterior wall and recessed 0.15 m; canyon street width 15 m with opposing block height varied to meet the target H/W; glazing visible transmittance 0.65; reflectances — ceiling 0.8, wall 0.5, floor 0.2, ground 0.1, façade 0.2.

---

## Data dictionary — `study/study.xlsx`

One row per simulated configuration (4,320 rows + header, sheet `Arkusz1`).

### Case identification and inputs

| Column | Type | Description |
|---|---|---|
| `Iteration_Nr` | int | Case index, 0–4319. Matches the `da-grids` image filename. |
| `DateTime` | datetime | Timestamp of the solver run. |
| `Location` | text | `Warsaw` or `Berlin`. |
| `Iteration_Name` | text | Encoded parameter combination, e.g. `Width0_Depth0_Window_height0_Urban_Canyon0_Direction0`. |
| `Win height` | float | Window head height in m (1.4 / 1.7 / 2.0). |
| `Depth` | int | Room depth in m (3–7). |
| `Width` | float | Room width in m (3.0–7.0). |
| `Area` | float | **Total enclosing surface area of the room in m² — not the floor area.** See the note below. |
| `Window area` | float | Glazed area in m². Always equals `Depth × Width / 8`. |
| `rotation` | int | Orientation **index**, not degrees: `0` = South (0°), `1` = West (90°), `2` = North (180°), `3` = East (270°). |
| `urban canyon toggle` | int | Density tier **index**, not the ratio itself: `0` = H/W 0.0 (unobstructed), `1` = H/W 0.5, `2` = H/W 1.0, `3` = H/W 1.5. |

> **Note on `Area`.** `Area` is the total internal surface area (floor + ceiling + four walls at 2.7 m height), which is why a 3.0 × 3.0 m room reports 50.4 m². The window-to-floor ratio is `Window area / (Depth × Width)` and equals 0.125 for every row. Dividing `Window area` by `Area` does **not** give the WFR.

### Results — `culled_*` columns are the reported metrics

Two variants of each metric are stored: one over the **full** sensor grid, and one over the **culled** grid, from which a 0.5 m perimeter band along the interior walls has been removed in line with ANSI/IES LM-83 practice. **All values reported in the manuscript come from the culled columns.**

| Column | Reported? | Description |
|---|---|---|
| `sDA` | – | sDA<sub>300/50%</sub> over the full grid, in % (0–100). |
| `culled_sDA` | **yes** | sDA<sub>unshaded;300/50%</sub> over the culled grid, in % (0–100). |
| `aDA` / `culled_aDA` | – | Mean daylight autonomy across the respective grid, in %. |
| `ASE_results` | – | ASE<sub>1000,250</sub> over the full grid, as a **fraction 0–1**. |
| `ASE_culled_results` | **yes** | ASE<sub>1000,250</sub> over the culled grid, as a **fraction 0–1**. Multiply by 100 for the percentages quoted in the manuscript. |
| `raw_DA` / `culled_raw_DA` | – | Per-sensor daylight autonomy, `;`-delimited, in %. |
| `raw_UDI` / `culled_raw_UDI` | – | Per-sensor Useful Daylight Illuminance, `;`-delimited, in %. |
| `raw_cDA` / `culled_raw_cDA` | – | Per-sensor continuous daylight autonomy, `;`-delimited, in %. |
| `raw_ASE_hours` / `raw_culled_ASE_hours` | – | Per-sensor count of hours above 1,000 lx of direct sun, `;`-delimited. |

### Sensor grid conventions

Workplane height 0.8 m, grid spacing 0.25 m.

- Full grid point count = `(Depth / 0.25) × (Width / 0.25)` — e.g. 144 points for a 3.0 × 3.0 m room, 784 for 7.0 × 7.0 m.
- Culled grid point count = `((Depth − 1) / 0.25) × ((Width − 1) / 0.25)` — the 0.5 m band is removed on all four sides.
- The `ASE_*` fractions are exactly (sensors exceeding the threshold) / (sensors in that grid); e.g. `ASE_culled_results = 0.234375` for case 0 is 15 of 64 culled sensors.
- Point ordering in the `;`-delimited fields follows the grid output of the parametric definition: *[to be stated explicitly — origin corner and traversal direction]*.

---

## Simulation setup

| Item | Setting |
|---|---|
| Modelling environment | Rhinoceros 3D / Grasshopper |
| Simulation toolset | Ladybug Tools (Ladybug + Honeybee), iterated with Colibri |
| Engine | Radiance |
| Radiance parameters | `-ab 5 -ad 5000 -lw 2e-05` |
| Sky | Perez All-Weather model via `gendaymtx`, Tregenza subdivision (145 sky patches + 1 ground patch, `gendaymtx -m 1`) |
| Climate files | EnergyPlus EPW: Warsaw-Okęcie (123750), Berlin (103840) |
| Evaluation window | 08:00–18:00, per ANSI/IES LM-83-23 |
| Shading | None. Metrics are unshaded — no dynamic blind model is applied. |

Because no occupant blind operation is modelled, `culled_sDA` describes the bare performance of the envelope and canyon geometry. Values should be read as an optimistic bound relative to occupied conditions, where blinds would be deployed in response to the glare risk visible in the ASE columns.

---


## Scope and limitations of the dataset

- Single-side-lit rectangular rooms with one centred window only; no corner units, multi-aspect dwellings or multiple apertures.
- Opposing obstructions are modelled as continuous uniform extrusions (semi-infinite canyon), not porous real-world urban fabric with staggered heights, setbacks or intersections.
- Surface reflectances and glazing transmittance are fixed at the values listed above; darker finishes or lower-transmittance glazing would depress the results further.
- No dynamic shading or occupant behaviour model.


## Licence

Code is MIT ([LICENSE](LICENSE)). Data, figures and documentation are CC BY 4.0
([LICENSE-DATA](LICENSE-DATA)). Attribution is required for both.

## Acknowledgements

Simulation uses [Radiance](https://www.radiance-online.org/) through
[Ladybug Tools](https://www.ladybug.tools/) inside [Grasshopper 3D](https://www.grasshopper3d.com/)

## Citation

*[Citation and DOI to be added on acceptance.]*
