#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 17-07-2026 13.44.49
#

import sys; sys.dont_write_bytecode = True
from datetime import datetime
from pathlib import Path

### - project modules
# from .get_last_tag import get_last_tag
from pyLnLib import  get_logger, lnRun
logger=get_logger()

###################################################
# ---- changelog avanzato ----
###################################################
# def generate_changelog(version: str, fExecute: bool, gitRoot: str):
def generate_changelog(git_prj: lnDict):
    changelog_path = git_prj.path / "CHANGELOG.md"
    last_tag = "v0.0.0"

    # trova ultimo tag nel changelog
    if changelog_path.exists():
        with open(changelog_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("## v"):
                    # last_tag = line.split()[1].lstrip("v")
                    last_tag = line.split()[1]
                    break
    else:
        last_tag = get_last_tag(gitRoot=gitRoot)

    log_range = f"{last_tag}..HEAD" if last_tag else "HEAD"
    log_range = "HEAD"

    # prendi commit reali (no merge) e filtra release/chore/docs
    _rcode, stdout, _stderr = lnRun(f'git log {log_range} --pretty=format:"%s" --no-merges', cwd=gitRoot, fExecute=True)
    commits_raw = stdout.splitlines()

    if not commits_raw:
        logger.info("Nessun commit rilevante per il changelog.")
        return False

    features, fixes = [], []
    for c in commits_raw:
        lc = c.lower()
        if lc.startswith("feat:"):
            features.append(c[5:].strip())
        elif lc.startswith("fix:"):
            fixes.append(c[4:].strip())
        elif lc.startswith("chore:") or lc.startswith("docs:") or lc.startswith("release"):
            continue
        else:
            fixes.append(c.strip())

    if not features and not fixes:
        logger.info("Nessun commit rilevante dopo filtro, skip changelog.")
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    new_section = f"## v{version} - {today}\n\n"

    if features:
        new_section += "### Features\n" + "\n".join(f"- {f}" for f in features) + "\n\n"
    if fixes:
        new_section += "### Fixes\n" + "\n".join(f"- {f}" for f in fixes) + "\n\n"

    if not fExecute:
        # preview colorata
        logger.notify("=== CHANGELOG.md preview ===")
        for line in new_section.splitlines():
            logger.info(line)
    else:
        old_content = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else ""
        changelog_path.write_text(new_section + old_content, encoding="utf-8")
        logger.notify("CHANGELOG.md aggiornato.")

    return True
