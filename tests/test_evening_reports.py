"""stats/evening_reports.py: the brief and the digest are written without a model (System 104, 2026-11-15)."""
from datetime import date

from stats import evening_reports as er

D = date(2026, 11, 14)


def _job(name, calls, fail=False, make=True):
    def path_of(d, reports):
        return reports / f"{name}-{d.isoformat()}.md"

    def write(d):
        calls.append(name)
        if fail:
            raise SystemExit("boom")
        if make:
            path_of(d, write.reports).write_text("x\n")
    return (name, path_of, write)


def _jobs(tmp_path, calls, **kw):
    jobs = [_job("brief", calls, **kw.get("brief", {})), _job("digest", calls, **kw.get("digest", {}))]
    for _n, _p, w in jobs:
        w.reports = tmp_path
    return jobs


def test_writes_both_once_and_leaves_existing_files_alone(tmp_path, capsys):
    calls = []
    assert er.run(D, jobs=_jobs(tmp_path, calls), reports=tmp_path) == 0
    assert calls == ["brief", "digest"]
    assert er.run(D, jobs=_jobs(tmp_path, calls), reports=tmp_path) == 0      # second run the same day
    assert calls == ["brief", "digest"]                                        # nothing ran twice
    assert "already written" in capsys.readouterr().out


def test_one_failing_report_never_stops_the_other(tmp_path, capsys):
    calls = []
    assert er.run(D, jobs=_jobs(tmp_path, calls, brief={"fail": True}), reports=tmp_path) == 1
    assert calls == ["brief", "digest"] and (tmp_path / "digest-2026-11-14.md").exists()
    assert "brief: FAILED SystemExit" in capsys.readouterr().out


def test_dry_run_writes_nothing(tmp_path):
    calls = []
    assert er.run(D, dry_run=True, jobs=_jobs(tmp_path, calls), reports=tmp_path) == 0
    assert calls == [] and list(tmp_path.iterdir()) == []


def test_real_paths_match_what_the_two_scripts_save():
    assert er.brief_path(D).name == "daily-brief-2026-11-14.md"
    assert er.digest_path(D).name == "socials-digest-2026-11-14.md"
