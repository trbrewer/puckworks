# Governing review findings

- `REVIEW-C1R4-001` (MAJOR): producer and independent verifier validate reached apparatus evidence but accept globally invalid supplied records. Reproduced cases are a dangling comparison before `NOT_EVALUATED`, an orphan cross-case prediction beside PASS, and a self-consistent caller-controlled contract-provenance mutation beside PASS.
- `REVIEW-C1R4-002` (MAJOR): hash `ade8df...` is a replay at milestone `61cafb5...`; two replays at final C1-R4 HEAD `206b9ac...` instead produce `4a23565e...`.

Governing review technical hash: `afb2b48bef9b0e055a22343991f7f2f1de68a6834631f380ef3259a336ce0eb6`. Final-review hash: `31102b3cc454c9df11a4f193a5a882b625517765215459f0614a6e33a0ffd9d4`.

Unaffected C1-R4 reached-path evidence closure and actual-pilot scientific state remain inputs to reverify, not assumptions to force.
