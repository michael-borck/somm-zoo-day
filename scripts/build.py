#!/usr/bin/env python3
"""Regenerate the derived parts of the companion site.

Three things in docs/ are derived rather than hand-written, and this script is
what derives them:

  * the QR codes, from the two URLs below;
  * assets/coverage.json, from the udl-lens checkpoint data;
  * the copy of that JSON inlined into index.html.

The coverage data is read straight out of the udl-lens repo so the site cannot
quietly drift from what the tool actually asks. If that repo has moved, pass
--lens; if the mapping has changed, rerun this and commit the result.

The page inlines its data rather than fetching it so that index.html works when
opened from disk - handy when the venue wifi does not cooperate.
"""

import argparse
import json
import pathlib
import shutil
import sys

# The QR points at the slinkr alias, not the Pages URL. slinkr refuses to
# repoint an existing alias, so this one is now permanent - but the site it
# resolves to can move without invalidating anything already printed.
SITE_URL = "https://slinkr.link/udl"
LENS_URL = "https://udllens.eduserver.au/"

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DEFAULT_LENS = ROOT.parent.parent.parent / "lens" / "udl-lens"

# The nine guidelines in CAST's published order. Fixed here rather than derived,
# because a guideline nothing maps to yet still has to appear as a gap - that is
# the whole point of the coverage view.
GUIDELINES = [
    ("Engagement", ["Welcoming Interests & Identities", "Sustaining Effort & Persistence",
                    "Emotional Capacity"]),
    ("Representation", ["Perception", "Language & Symbols", "Building Knowledge"]),
    ("Action & Expression", ["Interaction", "Expression & Communication",
                             "Strategy Development"]),
]

# Published for download. Everything else stays local - see .gitignore.
PUBLIC_FILES = [
    "UDL_Lens_Showcase_Leavebehind.docx",
    "UDL_Lens_iSoLT_Handout_v2.docx",
    "UDL3_Coverage_Map_for_review.docx",
    "UDL_Lens_ZooDay_Print_Materials.docx",
    "UDL_Lens_Showcase_AI_half_v1.pptx",
]


def build_coverage(lens_repo: pathlib.Path) -> dict:
    source = lens_repo / "data" / "udl-checkpoints.json"
    if not source.exists():
        sys.exit(f"No checkpoint data at {source}. Pass --lens with the udl-lens repo path.")

    data = json.loads(source.read_text())
    checkpoints = data["checkpoints"]
    type_ids = data["assessmentTypes"]
    labels = data["_meta"]["assessmentTypes"]

    order = [g for _, group in GUIDELINES for g in group]
    types = []
    for key, ids in type_ids.items():
        reached = sorted({checkpoints[i]["guideline"] for i in ids}, key=order.index)
        types.append({
            "key": key,
            "label": labels[key]["label"],
            "lane": labels[key].get("lane"),
            "guidelines": reached,
            "n": len(ids),
        })
    types.sort(key=lambda t: t["label"])

    return {
        "guidelines": [{"principle": p, "name": g} for p, group in GUIDELINES for g in group],
        "types": types,
    }


def build_qr_codes() -> None:
    try:
        import segno
    except ImportError:
        sys.exit("segno is not installed. pip install segno")

    for name, url in [("qr-companion", SITE_URL), ("qr-udllens", LENS_URL)]:
        # Error correction H so a code still scans with a logo over it, or off a
        # projector screen at the back of a room.
        code = segno.make(url, error="h")
        code.save(DOCS / "assets" / f"{name}.svg", scale=6, border=2, dark="#0F2530")
        code.save(DOCS / "assets" / f"{name}.png", scale=14, border=2, dark="#0F2530")
        print(f"  {name}.svg/.png  ->  {url}")


def inline_coverage(coverage: dict) -> None:
    """Put the JSON into the <script type="application/json"> block in index.html.

    Rewrites whatever is currently between the tags, so this is safe to run
    repeatedly - the first build substitutes a __COVERAGE__ placeholder, later
    ones replace the previous payload.
    """
    page = DOCS / "index.html"
    html = page.read_text()
    open_tag = '<script id="coverageData" type="application/json">'
    close_tag = "</script>"

    start = html.find(open_tag)
    if start == -1:
        sys.exit("Could not find the coverageData script block in index.html.")
    start += len(open_tag)
    end = html.find(close_tag, start)

    payload = json.dumps(coverage, indent=1)
    page.write_text(html[:start] + payload + html[end:])
    print(f"  index.html   ->  {len(payload)} bytes of coverage data inlined")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lens", type=pathlib.Path, default=DEFAULT_LENS,
                        help="path to the udl-lens repo (default: %(default)s)")
    args = parser.parse_args()

    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    (DOCS / "files").mkdir(parents=True, exist_ok=True)

    print("QR codes:")
    build_qr_codes()

    print("Coverage:")
    coverage = build_coverage(args.lens)
    (DOCS / "assets" / "coverage.json").write_text(json.dumps(coverage, indent=1))
    reach = max(len(t["guidelines"]) for t in coverage["types"])
    print(f"  coverage.json -> {len(coverage['types'])} assessment types, "
          f"best single-type reach {reach} of 9 guidelines")
    inline_coverage(coverage)

    print("Downloads:")
    for name in PUBLIC_FILES:
        source = ROOT / name
        if not source.exists():
            print(f"  MISSING {name} - skipped")
            continue
        shutil.copy2(source, DOCS / "files" / name)
        print(f"  {name} ({source.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    main()
