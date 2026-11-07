"""Build Amir's IG voice profile + collaborator list from IG data exports.

One-time / refreshable. Reads data/instagram-*/your_instagram_activity and writes
scene_intelligence/ig_voice_profile.json + ig_collaborators.json. Stdlib only.
"""
import json
import glob
import re
import argparse
import collections
import os

EXPORT_GLOB = "data/instagram-*/your_instagram_activity"
OUT_DIR = "scene_intelligence"


def fix_ig_text(s):
    """IG exports store UTF-8 re-decoded as latin-1. Reverse it. Safe on plain text."""
    if not isinstance(s, str) or not s:
        return s or ""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def collect_titles(obj, out):
    """Recursively collect every non-empty 'title' string value, encoding-fixed."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "title" and isinstance(v, str) and v.strip():
                out.append(fix_ig_text(v))
            else:
                collect_titles(v, out)
    elif isinstance(obj, list):
        for item in obj:
            collect_titles(item, out)


MENTION_RE = re.compile(r"@([A-Za-z0-9._]{2,30})")
HASHTAG_RE = re.compile(r"#(\w+)")
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]",
    flags=re.UNICODE,
)


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_captions(export_glob=EXPORT_GLOB):
    """Captions from posts_1.json, reels.json, stories.json across all exports. Deduped."""
    captions = []
    for base in glob.glob(export_glob):
        for name in ("media/posts_1.json", "media/reels.json", "media/stories.json"):
            for path in glob.glob(os.path.join(base, name)):
                collect_titles(_load_json(path), captions)
    seen, out = set(), []
    for c in captions:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def load_comment_owners(export_glob=EXPORT_GLOB):
    """Handles of accounts whose posts Amir commented on (engagement signal)."""
    owners = []
    for base in glob.glob(export_glob):
        for path in glob.glob(os.path.join(base, "comments/post_comments_1.json")):
            for item in _load_json(path):
                smd = item.get("string_map_data", {}) if isinstance(item, dict) else {}
                owner = smd.get("Media Owner", {}).get("value")
                if owner:
                    owners.append(fix_ig_text(owner))
    return owners


def build_voice_profile(captions):
    """Voice corpus + quantitative stats. Tone is interpreted later by the agent."""
    lengths = [len(c) for c in captions]
    hashtags = collections.Counter()
    emoji_captions = 0
    for c in captions:
        hashtags.update(h.lower() for h in HASHTAG_RE.findall(c))
        if EMOJI_RE.search(c):
            emoji_captions += 1
    return {
        "caption_count": len(captions),
        "avg_caption_chars": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "emoji_caption_ratio": round(emoji_captions / len(captions), 2) if captions else 0,
        "top_hashtags": hashtags.most_common(20),
        "captions": captions,  # raw examples for the agent to read
    }


SELF_HANDLES = {"inch_of_shadow"}


def build_collaborators(captions, comment_owners, exclude=SELF_HANDLES):
    """Rank credited accounts: @mentions in captions + accounts Amir comments on.

    Amir's own handle is excluded (it appears in his track-ID lists, not as a collaborator).
    """
    counts = collections.Counter()
    for c in captions:
        counts.update(m.lower() for m in MENTION_RE.findall(c))
    for owner in comment_owners:
        counts[owner.lower()] += 1
    for h in exclude:
        counts.pop(h.lower(), None)
    accounts = [{"handle": h, "count": n} for h, n in counts.most_common()]
    return {"accounts": accounts}


def main():
    ap = argparse.ArgumentParser(description="Build IG voice profile + collaborators")
    ap.add_argument("--export-glob", default=EXPORT_GLOB)
    ap.add_argument("--out-dir", default=OUT_DIR)
    args = ap.parse_args()

    captions = load_captions(args.export_glob)
    owners = load_comment_owners(args.export_glob)
    if not captions:
        raise SystemExit("No captions found. Check that IG exports exist under data/instagram-*")

    profile = build_voice_profile(captions)
    collab = build_collaborators(captions, owners)

    vp_path = os.path.join(args.out_dir, "ig_voice_profile.json")
    co_path = os.path.join(args.out_dir, "ig_collaborators.json")
    with open(vp_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    with open(co_path, "w", encoding="utf-8") as f:
        json.dump(collab, f, ensure_ascii=False, indent=2)

    print(f"Wrote {vp_path}: {profile['caption_count']} captions, "
          f"{len(profile['top_hashtags'])} hashtags")
    print(f"Wrote {co_path}: {len(collab['accounts'])} credited accounts")


if __name__ == "__main__":
    main()
