# Add MIT license (issue #106)

- Goal: answer #106 (zeuner, a nixpkgs packager) by licensing the repo under MIT.
- State: LICENSE added (Copyright 2026 Christopher Toth); pyproject.toml has
  `license = "MIT"` and `license-files = ["LICENSE"]` (PEP 639, hatchling).
- Decisions: Q chose MIT on 2026-10-19. No third-party code is tracked in git
  (no C/C++ sources or binaries; CaDiCaL under tools/solvers is untracked), and
  Q is the sole human author, so no other notices are needed.
- Surprises: the published 0.3.0 release has no license metadata; packagers need
  a new release or a statement on the issue that MIT covers earlier versions.
- Next step: PR CI, merge, reply on #106.
