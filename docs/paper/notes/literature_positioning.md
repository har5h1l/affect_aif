# Literature Positioning

## Foundation: Affect as Expected Precision

The closest theoretical foundation is Hesp et al.'s "Deeply Felt Affect," which
models affective valence as a hierarchical active-inference process involving
expected action precision and subjective model fitness:

- Hesp et al., "Deeply Felt Affect: The Emergence of Valence in Deep Active
  Inference" ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8594962/),
  [PubMed](https://pubmed.ncbi.nlm.nih.gov/33253028/)).

This project extends that account from one action-model precision signal to
multiple partner-local social model-fitness signals.

## Active Inference In Psychology And Psychiatry

Recent reviews argue that active inference is promising but needs precise,
testable model commitments and empirical discipline:

- Badcock and Davey, "Active Inference in Psychology and Psychiatry: Progress
  to Date?" ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11507080/)).
- The 2024 empirical-status review in *Neuroscience & Biobehavioral Reviews*
  emphasizes careful evidence claims and falsifiable model tests
  ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0149763423004426)).

The H0-H5 behavior cards respond to that need by turning the theory into
specific readouts: policy entropy, model-fitness dissociation, deployment
lesion, social choice, stress misdeployment, and perturbation dynamics.

## Multi-Agent Active Inference

Recent multi-agent work increasingly models other agents explicitly. The most
direct comparison is factorised active inference for strategic multi-agent
interactions, which gives agents individual-level beliefs about other agents
for strategic planning:

- "Factorised Active Inference for Strategic Multi-Agent Interactions"
  ([arXiv](https://arxiv.org/abs/2411.07362),
  [AAMAS 2025 proceedings](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1793.pdf)).

This project is complementary. Its main contribution is not a general
multi-agent planning algorithm; it is the partner-local affective precision
signal and the behavioral tests that separate model fitness from reward.

## Active Inference And Trust

Trust has already been modeled with active-inference POMDPs, especially in
human-automation contexts:

- Wei et al., "Is trust a belief, observation, or state: Results from an active
  inference analysis of driver-automation transitions of control"
  ([Sage](https://journals.sagepub.com/doi/abs/10.1177/21695067231192220)).
- Wei et al., active-inference models of automated-vehicle takeovers
  ([Sage](https://journals.sagepub.com/doi/pdf/10.1177/00187208241295932)).

Therefore the manuscript should not claim to be the first active-inference
model of trust. The narrower novelty claim is stronger: partner-specific
affective precision is separated from reward and from a dedicated trust scalar,
then tested as a deployment mechanism in a volatile multi-partner trust task.

## Novelty Claim

The manuscript can credibly claim novelty on four points:

1. Extending Hesp-style expected action precision to partner-local social model
   fitness.
2. Implementing that extension around official `pymdp` POMDP agents rather than
   a custom active-inference engine.
3. Testing model-fitness precision against reward, deployment lesion, social
   choice, and betrayal stress readouts.
4. Showing a productive boundary condition: affective precision can sharpen
   wrong deployment under abrupt social shocks.

## Claims To Avoid

Avoid claiming:

- a general solution to multi-agent active inference;
- a validated clinical model;
- a first model of active-inference trust;
- monotonic reward improvement from affect;
- human empirical support.
