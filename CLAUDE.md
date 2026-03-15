# Claude Working Notes

- Use the docs as the source of truth, but do not assume they are current. Verify against the code, then update both if they diverge.
- For theory or mechanism edits, check `docs/theory.md` and `docs/experiment.md` first.
- For environment, switching, or analysis changes, check `docs/implementation.md` first.
- For setup or usage changes, check `README.md` first.
- Every meaningful code change should leave the docs more accurate than before.
- Every behavior change should ship with tests or updated existing tests.
