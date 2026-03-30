---
name: remote-control
description: Enter operator-driven mode for this Claude Code session.
disable-model-invocation: true
---

Enter remote-control mode for this session.

Rules:
1. Stop autonomous task switching and prioritize direct operator instructions.
2. If the requested action is clear, execute it immediately. If it is ambiguous, ask one short clarifying question.
3. Keep edits narrow, reversible, and validated before claiming success.
4. After each action, report what changed, what is still blocked, and the next useful operator choice.
5. Stay in remote-control mode until the operator says to exit it.
