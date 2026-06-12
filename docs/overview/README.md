# Model Overview

This project extends Hesp et al.'s affect-as-expected-action-precision account
into multi-partner social active inference. See `core/hypotheses.md` for the
project goal, mechanism chain, and H0–H8 behavior cards.

## Three Layers

1. **Partner-type inference:** each partner has a local pymdp `Agent` whose
   state posterior tracks partner type and stance.
2. **Affective precision:** external beta dynamics track partner-action
   surprisal for the active partner.
3. **Policy deployment:** beta-derived policy precision changes how decisively
   existing beliefs are expressed in action.

The tracked-only lesion (`affect = tracked_only`) preserves inference while
decoupling beta from `gamma_k` — a computational analogue of knowing-versus-using
dissociations, not a literal neural model.

## Simulation Boundary

- **Focal AIF, scripted partners:** one focal agent against environment-side
  parameterized partners; partners do not run pymdp or affective precision.
- **Reciprocal AIF:** future work in `experiments/multifocal/`; not part of
  the current paper evidence.
- **Clinical-like variants:** perturbations of precision parameters — computational
  profiles, not validated diagnoses.

## Subfolders

### `core/` — canonical spine

Read these first. They are the supported public model surface.

| File | Contents |
|---|---|
| `hypotheses.md` | Project goal, mechanism chain, H0–H8 behavior cards |
| `pomdp.md` | Generative model (A/B/C/D/E), partner env, runtime cycle |
| `affective_precision.md` | Surprisal update, beta posterior, gamma deployment, modes |

### `background/` — optional deep reading

| File | Contents |
|---|---|
| `literature_review.md` | Long-form background (Damasio, Hesp, multi-agent AIF) |
| `pomdp_spec.md` | Detailed POMDP specification (v4, external precision tracking) |

Implementation: `tasks/trust/` (model + runtime), `experiments/trust/` (runs).
