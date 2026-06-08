# Model

The trust model separates three layers:

1. **Partner-type inference:** each partner has a local pymdp `Agent` whose
   state posterior tracks partner type and stance.
2. **Affective precision:** external beta dynamics track prediction error for
   the active partner.
3. **Policy deployment:** beta-derived policy precision changes how decisively
   existing beliefs are expressed in action.

Start with `pomdp.md` for the generative model, `affective_precision.md` for
the beta/gamma mechanism, and `hypotheses.md` for the paper claim spine.
