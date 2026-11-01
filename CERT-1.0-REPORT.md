# emailsyntax 1.0.0 certification report

Preparation for 1.0.0, dated 2026-11-01. The baseline is main at
75105c508bb6017c0464be4c5e0a57d63d6b9592. PyPI JSON fetched on this date reports 0.2.0.

Progress:
- [x] Review existing API and preserve ten public names and signatures.
- [x] Correct quoting, Unicode labels, literal syntax and error handling.
- [x] Add runnable examples, strict typing, contracts and seeded reference checks.
- [x] Update README, GUIDE, dated CHANGELOG and 1.0.0 package metadata.
- [x] Build and exercise a wheel in a fresh environment, including its CLI.
- [x] Install PyPI 0.2.0 and verify the upgrade in place.
- [x] Inspect distributions and run every installed supported interpreter.
- [x] Run and record at least ten deliberate mutations.
- [x] Run final gates and prepare pull request #3 from `release/1.0.0` to `main`.
- [x] Fix all 15 round-one QA findings and kill the six surviving mutations.
- [x] Fix C-05 and close the E-07 mutation gap from round two.
- [x] Close the E-08 subclass slicing contract gap from round three.
- [x] Close the E-09 and E-10 subclass conversion contract gaps from round four.
- [x] Close the E-11 through E-15 subclass conversion contract gaps from round five.
- [ ] Independent review (item 16), merge/publication (item 17), five QA lenses (item 19).

## API and tests

The public API, flags, defaults, value fields and failure codes remain available. Every
behavior change is listed in CHANGELOG 1.0.0. Direct dataclass construction remains an
unchecked value-container operation. The reserved `domain_too_long` reason cannot be reached
through public validation because the whole-address bound is tighter.

Baseline format, lint and strict typing passed; 78 non-e2e tests passed. After the changes,
137 tests pass with the fetched sources, including wheel installation, CLI subprocesses,
examples for all ten public names, README/GUIDE examples, 10,000 grammar cases, 1,000 generated
valid addresses against `email.headerregistry.Address`, 1,000 IP reference cases and 5,000
Unicode fuzz cases. Tests use a 300-second per-test timeout.

## Ground truth

Fetched on 2026-11-01: RFC 5321, RFC 5322, RFC 6531, Python 3.14 codec documentation and
email-validator PyPI metadata. `sources/MANIFEST.json` records URLs, dates, sizes, hashes
and licenses. External contents stay outside the distribution; `scripts/fetch_sources.py`
retrieves and verifies them into a caller-selected directory. Set `EMAILSYNTAX_SOURCES` to
that directory to check hashes during the suite; that check skips when it is absent.

The short RFC 5322 Appendix A.1.1 address in `test_oracle.py` was copied from the fetched
text. Quoted-pair and length cases are explicitly derived from the fetched RFC 5321 grammar,
not presented as official vectors. Python's `email.headerregistry.Address` and `ipaddress`
run as independent reference implementations on the documented overlapping syntax.

Unicode mode deliberately retains Python's IDNA 2003 compatibility policy. It does not
claim full IDNA 2008, SMTPUTF8, HTML input or RFC 5322 grammar conformance.


## Preparation scorecard

| Item | Result and evidence |
| --- | --- |
| 1 | PASS: names, signatures, defaults and result fields pinned; behavior differences in CHANGELOG |
| 2 | PASS: exact `__all__` and no extra non-private package attributes |
| 3 | PASS: public doctests plus executable README/GUIDE examples |
| 4 | PASS: `mypy --strict src tests`; typed external wheel consumer; shipped `py.typed` |
| 5 | PASS: fixed input-free messages, typed syntax errors and wrong-type errors |
| 6 | PASS: 137 contracts, examples, reference checks and wheel/CLI tests |
| 7 | PASS: live-fetched specifications with manifest, derived grammar tests and running references |
| 8 | PASS: wheel in fresh venv, CLI subprocesses, sdist install, actual PyPI upgrade |
| 9 | PASS: fixed seeds, random Unicode, generated ASCII and IP cases; scaling below |
| 10 | PASS for available interpreters: 3.11.11 and 3.14.6; unavailable versions listed below |
| 11 | PASS: absolute README links, honest comparison, `twine check --strict` |
| 12 | PASS: 1.0.0 section dated 2026-11-01 |
| 13 | PASS: 1.0.0, Production/Stable, Python classifiers, MIT, URLs, no runtime dependencies |
| 14 | PASS: contents of both archives inspected, license and typing marker included |
| 15 | PASS: four commands run separately; final results below |
| 16 | PENDING: independent review |
| 17 | PR #3 ready; merge and publication reserved for maintainer |
| 18 | PASS: 20 isolated deliberate mutations, all caught |
| 19 | PENDING re-review: five round-one FAIL verdicts; all reported findings addressed below |

## Packaging, upgrade and interpreter results

The built wheel contains eight Python modules, `py.typed`, metadata, entry points and LICENSE.
The sdist contains the package, reusable tests, README/GUIDE/CHANGELOG, manifest and fetch
script, pyproject, LICENSE, PKG-INFO and Hatchling's automatically included `.gitignore`.
Neither archive contains fetched third-party content, scratch files, caches or process reports.
`python -m build` built the wheel from the sdist. Both pass `twine check --strict`.
A separate fresh environment installed the sdist, executed the typed consumer and drove the CLI.

The actual PyPI 0.2.0 wheel was downloaded and installed in a fresh environment. Its Python
modules match `main` byte for byte after newline normalization. Upgrading that environment
in place to the local 1.0.0 wheel preserved all ten exports, six function signatures and
ordinary/quoted parsed results. Before/after executions confirmed each category of changed
validation: escaped controls/non-ASCII, scoped IPv6, literal-tag case, mapped IDNA separators
and symbols, Unicode local octets, encoded address size, and oversized-input error precedence.
Wrong-type and wrong-flag errors, input-free messages and exception pickle support were also
checked against both installed versions. The upgraded console script reports 1.0.0.

| Interpreter | Suite against installed wheel | CLI |
| --- | --- | --- |
| CPython 3.14.6, system installation | 137 passed | PASS |
| CPython 3.11.11, Blender 4.5.10 bundled runtime | 137 passed | PASS |

For each interpreter, the suite came from the extracted sdist, with pytest's `pythonpath`
cleared. A separate isolated consumer asserted the import came from `site-packages`.
The e2e fixture installed the same wheel into another fresh venv and drove its executable.
A standalone external consumer also passed `mypy --strict` against the installed wheel.

Python 3.10, 3.12, 3.13 and free-threaded Python could not be run: the launcher entries
point at deleted installations. All thirteen non-system registered paths were checked and
absent; the six user-local launchers also fail because their targets are missing. No new
interpreter installation was required. Python 3.9 and below are outside `requires-python`.

## Robustness and mutation results

The committed suite uses seeds 20261101, 6531 and 5322. Oversized inputs are rejected before
character scanning or IDNA conversion. A separate scaling run used 1,000, 10,000, 100,000
and 1,000,000 characters of `@`, backslash and Unicode text: 1,000 validations took
0.0037 to 0.0055 seconds across sizes. Ten normalizations with surrounding whitespace took
0.00015, 0.00055, 0.00234 and 0.02958 seconds respectively, consistent with linear trimming.
These are observations from this machine, not timing assertions in the suite.

Each deliberate mutation below was applied alone in a scratch copy, bytecode disabled,
and the contract/CLI suite was run with `-x` and a 300-second timeout. No syntax or collection
errors count as kills. All 20 failed on a behavioral assertion; no survivor remained. The
source tree was not mutated. The normal full suite passed before and after the round.

| Id | Mutation | Caught by |
| --- | --- | --- |
| M01 | local boundary | `test_lengths_measure_utf8_local_and_idna_domain` |
| M02 | address boundary | `test_lengths_measure_utf8_local_and_idna_domain` |
| M03 | label boundary | `test_lengths_measure_utf8_local_and_idna_domain` |
| M04 | ASCII restriction | `test_failure_contract` |
| M05 | split first at | `test_result_objects_are_frozen_values` |
| M06 | local case changed | `test_json_has_complete_result_fields` |
| M07 | domain case unchanged | `test_json_has_complete_result_fields` |
| M08 | boolean inverted | `test_strict_mode_accepts` |
| M09 | input leaked | `test_failure_contract` |
| M10 | wrong exception | `test_validate_or_raise_raises_typed_error` |
| M11 | quoted escape accepts controls | `test_optional_failure_codes` |
| M12 | zone identifier allowed | `test_optional_failure_codes` |
| M13 | dotless domain allowed | `test_strict_mode_rejects` |
| M14 | edge hyphen allowed | `test_strict_mode_rejects` |
| M15 | Unicode octets ignored | `test_lengths_measure_utf8_local_and_idna_domain` |
| M16 | IDNA output unchecked | `test_optional_failure_codes` |
| M17 | encoded address cap ignored | `test_lengths_measure_utf8_local_and_idna_domain` |
| M18 | normalize fails to trim | `test_split_and_normalize_still_work` |
| M19 | CLI strict ignored | `test_flags_and_strict_override` |
| M20 | CLI exit inverted | `test_json_has_complete_result_fields` |


## Gates and remaining stages

`ruff format --check .`, `ruff check .`, `mypy --strict src`, and `pytest` each exit 0.
The stronger `mypy --strict src tests` also exits 0. The full suite has 137 passing tests
when `EMAILSYNTAX_SOURCES` points to the fetched sources. Without that optional directory,
the source-hash check skips cleanly; behavioral contracts still run.

All test temporary paths and build temporary directories were explicitly placed in the
private scratch directory. The per-test timeout is 300 seconds. At most two heavy jobs
ran concurrently. The preparation stage preceded the QA lenses recorded below;
there are no carried-forward PASS verdicts. Merge and publication remain pending.

Pull request: https://github.com/JaviLianes8/emailsyntax/pull/3.
The final code and tests were verified at a8d2e65; the subsequent change only records this
pull request and the completed preparation checklist.

## QA lenses: round 1 fixes (2026-11-01)

Reviewed head: `7cca20e9aad2c68a13045a40fc63f9121615c116`. All five lenses reported FAIL.
Fix commit: `ded80779d209eb360f4174a066d06f49fa20ebac` (`fix round-one certification findings`).
All 15 findings are accepted; independent re-review is pending. No findings are disputed.

| Findings | Change and regression contract |
| --- | --- |
| A-01, B1, C-02 | Check normalized character and encoded limits before success; all six APIs reject lowercase overflow with `address_too_long`; adjacent accepted limits remain idempotent. |
| A-02, B2 | Correct GUIDE's hexadecimal-only promise; document interpreter-dependent mapped IPv6 formatting and execute examples of both input forms. No formatting behavior changed. |
| C-01 | Convert subclasses through `str.__str__` before overridable operations; all six APIs use the underlying string for parsing, result addresses and syntax errors. |
| C-03 | Malformed stdin exits 1 with a fixed input-free diagnostic and no results; both entry points tested in human, JSON and quiet modes. |
| C-04, D-01 | Escape unsupported stdout characters while retaining valid-input exit 0; both installed entry points tested with strict cp1252, ASCII and UTF-8. |
| E-01 | Assert all quoted-local result fields through `validate` and installed CLI JSON. |
| E-02 | Vary each `EmailAddress` field independently; assert inequality and separate set membership. |
| E-03 | Vary each `ValidationResult` field independently; assert inequality and separate set membership. |
| E-04 | Both installed entry points reject positional whitespace and preserve the exact JSON address. |
| E-05 | Both installed entry points trim tabs and Unicode whitespace around nonempty stdin lines. |
| E-06 | Assert raw JSON stdout is ASCII and contains Unicode escapes before decoding it. |

Before implementation changes, contracts reproduced 36 API and 10 CLI failing cases.
The API rerun corrected two fixture length calculations; those fixture errors are excluded.
After fixes, the targeted tests and documentation examples passed: 88 tests.
Evidence is retained under scratch `fix-r1/`: `red.log`, `red-corrected.log`, `green.log`.

The six lens-e mutations were replayed separately in scratch copies. Each failed on an
assertion, with no collection or setup failures: M17 quoted metadata (1 failure), M41
normalized equality (1), M42 IP-flag equality (1), M47 positional whitespace (8), M48 stdin
whitespace (6), M49 ASCII JSON (2). See `mutation-results.json` and `M17.log` through
`M49.log` in that scratch directory. The production source was not mutated.

Final gates: `ruff format --check .`, `ruff check .`, `mypy --strict src`, and `pytest`
all exit 0; `mypy --strict src tests` also passes. Full suite: 223 passed on Python 3.14.6
and 223 passed on Python 3.11.11, with fetched-source checks and installed-wheel CLI tests.
Logs: `full.log` and `python311.log`. Tests use pytest-timeout at 300 seconds and scratch
temporary directories. Other Python versions were not rerun in this fix stage.
CHANGELOG records every behavior change. Public names, signatures and defaults are unchanged.

## QA lenses: round 2 fixes (2026-11-01)

Reviewed head: `89cb624766d93ae28bd611525a429204e2b669d7`.
Fix commit: `8f1a4c2407709fa47eaa8a1a4d231fb50d33a248` (`fix round-two certification findings`).
Both findings are accepted; independent re-review is pending. No findings are disputed.

| Finding | Change and regression contract |
| --- | --- |
| C-05 | Check `issubclass(type(address), str)` before conversion. All six address APIs reject objects with raising or spoofed `__class__` properties using exactly `TypeError("address must be a string")`, without invoking those properties. String subclasses remain supported. |
| E-07 | Add installed module and console-script contracts for `josé@example.com` under `cp1252:strict`: exact stdout bytes including `0xe9`, empty stderr and exit 0. Existing CLI behavior is correct; this closes the missing contract. |

The C-05 contracts were added before the source fix: all 12 cases failed on the reviewed
code and pass after the type-gate change. The reviewer's original P12 repro also passes.
Targeted boundary and installed-CLI tests: 85 passed. Evidence is retained in scratch
`fix-r2/red-api.log`, `green.log` and `p12.log`.

N17 was replayed in an isolated scratch copy by replacing `.decode(encoding)` with
`.decode("utf-8")` in `_print_human`. The new contracts detected the mutation through
both entry points of a freshly built and installed wheel: 2 assertion failures because
the mutant exits 1 with `UnicodeDecodeError`. No collection or setup failure counted as
a kill. See `fix-r2/replay_n17.py` and `n17.log`. Production CLI code was not changed.

Final gates: `ruff format --check .`, `ruff check .`, `mypy --strict src` and `pytest`
each exit 0; `mypy --strict src tests` also passes. Full suite: 237 passed on Python 3.14.6,
including fetched-source hashes and fresh installed-wheel tests, with pytest-timeout at
300 seconds. TEMP, TMP and pytest basetemp were inside scratch `fix-r2/`; see `full.log`.
Other interpreters were not rerun in this bounded fix stage. CHANGELOG records the type-gate
behavior change and additional CLI contract. Public names, signatures and defaults are stable.

## QA lenses: round 3 fixes (2026-11-01)

Reviewed head: `def1c3e167a8f1ebfebc1493dfe34774577962cb`.
Fix commit: `16d5b2c3a9f509cef759717c437d7d1248e6008a` (`pin subclass slicing contracts`).
E-08 is accepted; independent re-review is pending. No findings are disputed.

| Finding | Change and regression contract |
| --- | --- |
| E-08 | Add 24 cases across all six address APIs with forged and raising `__getitem__` overrides, using valid and invalid underlying strings. Assert overrides are never called, results match the underlying value, invalid input reports `no_at`, and result/error addresses preserve the built-in string. |

The existing `str.__str__` conversion is correct, so production code and behavior are
unchanged. The new contracts pass on the reviewed implementation. CHANGELOG records the
added coverage; public names, signatures and defaults remain stable.

Replayed the reviewer's M17 in an isolated scratch copy, replacing
`return str.__str__(address)` with `return address[:]`. All 24 new cases fail: forged
values violate result, rejection or hook-call assertions, and raising overrides escape
as `RuntimeError`. There are no collection or setup errors. The scratch source was
restored after the replay; production source was never mutated. Evidence is retained in
scratch `fix-r3/replay_m17.py`, `m17.log`, `m17.xml` and `baseline.log`.

| Mutation | Caught by |
| --- | --- |
| Lens-e round 3 M17: copy input through an overridable slice | `test_subclass_slicing_never_overrides_underlying_input`, all 24 cases |

Final gates: `ruff format --check .`, `ruff check .`, `mypy --strict src` and `pytest`
each exit 0; `mypy --strict src tests` also passes. Full suite: 261 passed on Python 3.14.6,
including fetched-source hashes and fresh installed-wheel CLI tests. Tests use
pytest-timeout at 300 seconds; TEMP, TMP and pytest basetemp stay inside scratch `fix-r3/`.
See `full.log`. Other interpreters were not rerun in this bounded fix stage.

## QA lenses: round 4 fixes (2026-11-01)

Reviewed head: `efc34c602eacdd77fb98e60689065b52d3075813`.
Fix commit: `04310cae697a26d6c0684ce7b0e194a684c0ffca` (`pin subclass conversion contracts`).
E-09 and E-10 are accepted; independent re-review is pending. No findings are disputed.

| Finding | Change and regression contract |
| --- | --- |
| E-09 | Add 24 cases for forged and raising `__add__` overrides across all six address APIs, using valid and invalid underlying strings. Assert no override calls, results matching the underlying value, `no_at` rejection, and built-in result/error addresses. |
| E-10 | Add the same 24 cases for forged and raising `removeprefix` overrides across all six address APIs. |

These are contract gaps: the existing `str.__str__` conversion is correct. All 48 new
cases pass on the reviewed implementation. Production code and behavior are unchanged;
CHANGELOG records the additional coverage. Public names, signatures and defaults are stable.

Replayed N05 and N10 separately in a scratch copy after adding the contracts. Each mutant
fails all 24 applicable cases, while the other 24 cases pass. No collection or setup errors
count as kills. Original source bytes are restored after each replay; production source
was never mutated. Evidence is retained in scratch `fix-r4/replay.py`, `results.json`,
`baseline.log`, `N05.log`, `N10.log` and their corresponding XML reports.

| Mutation | Caught by |
| --- | --- |
| N05: replace `return str.__str__(address)` with `return address + ""` | `test_subclass_conversion_never_overrides_underlying_input`, all 24 `__add__` cases |
| N10: replace `return str.__str__(address)` with `return address.removeprefix("")` | `test_subclass_conversion_never_overrides_underlying_input`, all 24 `removeprefix` cases |

Final gates: `ruff format --check .`, `ruff check .`, `mypy --strict src` and `pytest`
each exit 0; `mypy --strict src tests` also passes. Full suite: 309 passed on Python 3.14.6,
including fetched-source hashes and fresh installed-wheel CLI tests. Tests use
pytest-timeout at 300 seconds; TEMP, TMP, TMPDIR and pytest basetemp stay inside scratch
`fix-r4/`. See `full.log`. Other interpreters were not rerun in this bounded fix stage.

## QA lenses: round 5 fixes (2026-11-01)

Reviewed head: `f0f55043c41025d01594ec055d820eb7c13ffd36`.
Fix commit: `pin remaining subclass conversion contracts` (this round's test commit).
All five findings are accepted; independent re-review is pending. No findings are disputed.

| Finding | Change and regression contract |
| --- | --- |
| E-11 | Add 24 cases for forged and raising `__mul__` overrides across all six address APIs. |
| E-12 | Add the same 24 cases for `replace` overrides. |
| E-13 | Add the same 24 cases for `removesuffix` overrides. |
| E-14 | Add the same 24 cases for `ljust` overrides. |
| E-15 | Add the same 24 cases for `rjust` overrides. |

Every hook is tested with valid and invalid underlying strings. Contracts assert zero
hook calls, results matching plain-string input, `no_at` rejection, and built-in string
result/error addresses preserving the underlying value. These are missing contracts,
not behavior defects in the reviewed implementation: all 120 additional cases pass with
the existing `str.__str__` conversion. Production code, behavior and public API are unchanged.
CHANGELOG records the added coverage.

Replayed all five reported mutations separately in a scratch copy after adding the tests.
Each fails all 24 applicable cases; the other 144 conversion cases pass. The baseline
passes all 168 cases. No collection, setup or skipped cases count as kills. Original
source bytes are restored after each replay; production source was never mutated.

| Mutation | Caught by `test_subclass_conversion_never_overrides_underlying_input` |
| --- | --- |
| M01: `return address * 1` | All 24 `__mul__` cases |
| M04: `return address.replace("", "")` | All 24 `replace` cases |
| M05: `return address.removesuffix("")` | All 24 `removesuffix` cases |
| M06: `return address.ljust(0)` | All 24 `ljust` cases |
| M09: `return address.rjust(0)` | All 24 `rjust` cases |

Evidence is retained in scratch `fix-r5/replay.py`, `results.json`, `baseline.log`,
`M01.log`, `M04.log`, `M05.log`, `M06.log`, `M09.log` and corresponding XML reports.

Final gates: `ruff format --check .`, `ruff check .`, `mypy --strict src` and `pytest`
each exit 0; `mypy --strict src tests` also passes. Full suite: 429 passed on Python 3.14.6,
including fetched-source hashes and fresh installed-wheel CLI tests. Tests use
pytest-timeout at 300 seconds; TEMP, TMP, TMPDIR and pytest basetemp stay inside scratch
`fix-r5/`. See `full.log`. Other interpreters were not rerun in this bounded fix stage.
