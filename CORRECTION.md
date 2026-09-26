# Corrections to the dataset

This version replaces the dataset released with the original submission of the manuscript. During the revision, all results were recomputed from the stored per-sensor arrays. This check found the errors listed below. No simulation had to be repeated: the per-sensor results were correct, and every metric was recomputed from them.

## 1. Normalisation of the culled sDA

In the original post-processing, sDA for the grid with a 0.5 m perimeter band removed (`culled_sDA`) was divided by the number of sensors in the **full** grid instead of the culled grid. All reported values were therefore too low, by a factor of 1.51 to 1.92 depending on room size.

- `culled_sDA` in Batches A and B has been recomputed with the correct denominator.
- The manuscript now reports sDA and ASE over the **full** floor area (`sDA`, `ASE_results`), as defined in ANSI/IES LM-83-23. The culled columns are kept for sensitivity analysis.
- The convergence file (`D-ab-sweep.xlsx`) was rebuilt in the same format. Its original `culled_sDA` column carried the same error.

Effect on the manuscript: mean sDA across Batch A is 22.44% (previously 15.68%); at H/W = 0.0, 1.0 and 1.5 it is 42.58%, 13.47% and 7.65% (previously 32.30%, 8.16% and 2.88%). The main finding, that street aspect ratio controls sDA, is unchanged.

## 2. Orientation labels

The model rotates counter-clockwise. `rotation` is therefore `0` South, `1` East, `2` North, `3` West. The original documentation listed `1` as West and `3` as East.

## 3. Sill height

The sill was 0.80 m for window clear heights of 1.4 m and 1.7 m, and 0.67 m for 2.0 m, so that the window head stays below the 2.70 m ceiling. The original documentation stated a fixed 0.80 m sill. The sill is now recorded per configuration in `sill_h`, and Batch B separates its effect from that of window clear height.

## 4. Visible transmittance

The glazing had a visible transmittance of 0.64 (Ladybug Tools generic exterior window material; Radiance transmissivity 0.6976), not 0.65 as originally documented.

## 5. Column names

- In the original Batch A file, the column names `raw_ASE_hours` and `raw_culled_ASE_hours` were swapped. They now match their contents. The reported ASE values were not affected.
- `Win height` is renamed `win_height` and documented as window **clear** height (sill to head), not head height.
- ASE is stored in percent (0 to 100) in all files. It was previously stored as a fraction (0 to 1).
- Each configuration has a `case_id` (`A-00000` …), which also names its image in `study/da-grids/`.

## Verification

```bash
python scripts/check_metrics.py
```

recomputes every stored sDA and ASE value from the per-sensor arrays, reports any difference, and prints the headline values quoted in the manuscript.
