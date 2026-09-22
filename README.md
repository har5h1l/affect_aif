# Partner-Specific Affective Precision in Social Active Inference

Active-inference trust-game simulations for studying partner-local affective
precision as a relationship-specific confidence signal.

Accepted as a full paper at the 7th International Workshop on Active
Inference (IWAI 2026). The public preprint is
[available on arXiv](https://arxiv.org/abs/2609.24876). This repository contains
the code, experiment configurations, results, and manuscript.

## What This Is

`affect_aif` contains a pymdp-backed trust-game model, paper reproduction
configs, compact result summaries, and the manuscript source. It studies
how confidence in each social partner shapes the agent's decisions.

## Code And Repository Map

| Area | Start here |
|---|---|
| User guide | [docs/guide/](docs/guide/README.md): reproduce, configure, and use notebooks or scripts. |
| Agent and environment | [tasks/](tasks/README.md): partner-local pymdp agents, confidence updates, and trust-game mechanics. |
| Experiment execution | [experiments/](experiments/README.md): config expansion, runtime construction, episode loop, and logging. |
| Analysis | [analysis/](analysis/README.md): metrics, statistics, profiles, and plots from existing data. |
| Commands | [scripts/](scripts/README.md): supported run, inspect, and analysis entry points. |
| Config files | [configs/](configs/README.md): paper, demo, diagnostic, and future TOML files. |
| Notebooks | [Notebook guide](docs/guide/notebooks.md): demo and full-reproduction walkthroughs. |
| Results | [Findings and provenance](docs/results/README.md); [data folders](results/README.md). |
| Manuscript | [main.tex](docs/manuscript/main.tex), bibliography, figures, and the compiled PDF. |
| Tests | [tests/](tests/README.md): implementation and interface checks. |

To follow one run through the code, start with `scripts/experiment/run.py`,
then `experiments/trust/spec.py` and `factory.py`, followed by
`experiments/trust/runner.py`. The runner calls the agent machinery in
`tasks/trust/runtime.py` and the environment under `tasks/trust/envs/`.
Once trajectories are written, the analysis scripts read them to produce
summaries. The package READMEs above identify the files for each step.

## Getting Started

- [Install and reproduce](docs/guide/reproduce.md): setup, a small demo,
  the full paper suite, and manuscript compilation.
- [Use the notebooks](docs/guide/notebooks.md): local and Colab walkthroughs.
- [Configure an experiment](docs/guide/configs.md): model controls, variants,
  sweeps, workloads, and output paths.
- [Run and analyze](docs/guide/running.md): CLI options, checkpoints, and
  post-hoc analysis.
- [Read the findings](docs/results/findings.md): measured results and limitations.

## Paper Result Data

Download the paper's results and verify the archive with its checksum:

- [`paper_results.zip`](paper_results.zip)
- [`paper_results.zip.sha256`](paper_results.zip.sha256)

See the [guide](docs/guide/reproduce.md#use-the-published-results-without-rerunning)
for extraction and analysis instructions.

## Citation

Built on [inferactively-pymdp](https://github.com/infer-actively/pymdp) for
belief updating and policy selection.

If you use the paper or this repository, please cite the arXiv preprint. A
machine-readable version is also available in [`CITATION.cff`](CITATION.cff).

```bibtex
@misc{shah2026partner,
  title         = {Partner-Specific Affective Precision in Social Active Inference},
  author        = {Shah, Harshil and Pashea, Andrew},
  year          = {2026},
  eprint        = {2609.24876},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  doi           = {10.48550/arXiv.2609.24876},
  url           = {https://arxiv.org/abs/2609.24876}
}
```

For implementation details, also cite the repository at the specific commit
used: <https://github.com/har5h1l/affect_aif>.

## License

Released under the [MIT License](LICENSE).
