# emailsyntax 1.0.0 certification report

Preparation for 1.0.0, dated 2026-11-01. The baseline is main at
75105c508bb6017c0464be4c5e0a57d63d6b9592. PyPI JSON fetched on this date reports 0.2.0.

Progress:
- [x] Review existing API and preserve ten public names and signatures.
- [x] Correct quoting, Unicode labels, literal syntax and error handling.
- [x] Add runnable examples, strict typing, contracts and seeded reference checks.
- [x] Update README, GUIDE, dated CHANGELOG and 1.0.0 package metadata.
- [x] Build and exercise a wheel in a fresh environment, including its CLI.
- [ ] Install PyPI 0.2.0 and verify the upgrade in place.
- [ ] Inspect distributions and run every installed supported interpreter.
- [ ] Run and record at least ten deliberate mutations.
- [ ] Run final gates and prepare the pull request.
- [ ] Independent review (item 16), merge/publication (item 17), five QA lenses (item 19).

## API and tests

The public API, flags, defaults, value fields and failure codes remain available. Every
behavior change is listed in CHANGELOG 1.0.0. Direct dataclass construction remains an
unchecked value-container operation. The reserved `domain_too_long` reason cannot be reached
through public validation because the whole-address bound is tighter.

Baseline format, lint and strict typing passed; 78 non-e2e tests passed. After the changes,
137 tests pass with the fetched sources, including wheel installation, CLI subprocesses,
10 public docstring examples, README/GUIDE examples, 10,000 grammar cases, 1,000 generated
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
