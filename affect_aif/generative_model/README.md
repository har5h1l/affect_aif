# Generative Model Layer

## Responsibility

This layer defines the trust-game generative models used by the supported experiments.

## Public Surface

The package-level import surface is `affect_aif.generative_model`. It re-exports:

- `TrustGameModel`
- `GradedTrustGameModel`
- `PartnerType`
- `PARTNER_TYPE_ORDER`

## Key Modules

- `model.py`: trust-game model classes and matrix assembly
- `payoffs.py`: payoff index tables and payoff structures
- `partner_types.py`: latent partner-type definitions and ordering

## Internal / Compatibility Notes

- The graded model is shipped alongside the binary trust-game model and is not an archive artifact.
- Model assembly stays in this package so the experiment layer can treat model construction as a narrow factory concern.
