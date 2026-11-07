"""
release_manager/email_outreach.py
-----------------------------------
Tool 4 -- Email Outreach Manager

Intelligent email composer that uses Scene Intelligence data to generate
deeply personalized outreach emails. Each email is assembled from context-aware
blocks -- no two emails should feel the same.

Templates:
  - label_pre:  Label demo submission (pre-release, private link)
  - label_post: Label outreach (post-release, public links)
  - media_pre:  Media/premiere pitch (pre-release)
  - followup:   Follow-up for non-responders

Design principles:
  - Deep personalization using SI data (boss name, genre, location, tier)
  - Focused: every sentence serves a purpose
  - Psychologically optimized: familiarity, relevance, curiosity, respect
  - Clean visual structure: short paragraphs, breathing room
  - Tone: professional, warm, artistic, confident, never arrogant
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
import smtplib
import ssl
import time
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.utils import formataddr
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_BASE_DIR = Path(__file__).parent.parent
load_dotenv(_BASE_DIR / ".env")

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
SENDER_NAME = "Inch of Shadow"

# Rate limiting — persisted so a webapp restart cannot reset the hourly
# budget (audit P4-24). File holds {"sends": [{"ts": float, "to": str,
# "subject": str}, ...]}, pruned to the last 24h on every write.
MAX_PER_HOUR = 20
MIN_INTERVAL_SEC = 3
SEND_STATE_FILE = _BASE_DIR / "release_manager" / "email_send_state.json"
_SEND_STATE_KEEP_SEC = 24 * 3600

# Attachments (audit P4-24): only files inside the project tree may be
# attached — the path arrives from the web client, and an unrestricted path
# would let a request email out ANY readable file (.env included). No hidden
# path components, and Gmail's ~25MB cap enforced locally.
ATTACHMENT_ROOT = _BASE_DIR
MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024


def _load_send_state() -> list[dict]:
    try:
        with open(SEND_STATE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        sends = data.get("sends", [])
        return sends if isinstance(sends, list) else []
    except (OSError, ValueError):
        return []


def _record_send(to_addr: str, subject: str) -> None:
    now = time.time()
    sends = [s for s in _load_send_state()
             if isinstance(s, dict) and s.get("ts", 0) > now - _SEND_STATE_KEEP_SEC]
    sends.append({"ts": now, "to": to_addr, "subject": subject})
    tmp = SEND_STATE_FILE.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"sends": sends}, f, indent=2, ensure_ascii=False)
    os.replace(tmp, SEND_STATE_FILE)


def find_recent_duplicate(to_addr: str, subject: str,
                          within_hours: float = 24.0) -> dict | None:
    """A same-recipient, same-subject send inside the window, or None.

    Double-send guard (audit P4-24): a success that failed to persist its
    status update, or a double-click, must not silently email the contact
    twice. send_email refuses these unless force=True.
    """
    cutoff = time.time() - within_hours * 3600
    for s in reversed(_load_send_state()):
        if (isinstance(s, dict) and s.get("ts", 0) > cutoff
                and s.get("to") == to_addr and s.get("subject") == subject):
            return s
    return None


_HEADER_BREAK_RE = re.compile(r"[\r\n]")


def _header_injection(value: str) -> bool:
    """True if a header value contains CR/LF (SMTP header injection)."""
    return bool(_HEADER_BREAK_RE.search(value or ""))


def validate_attachment(path_str: str) -> dict:
    """Validate a client-supplied attachment path.

    Returns {"ok": True, "path": resolved} or {"ok": False, "error": ...}.
    """
    try:
        resolved = Path(path_str).resolve()
    except (OSError, ValueError):
        return {"ok": False, "error": "Attachment path could not be resolved"}
    try:
        rel = resolved.relative_to(ATTACHMENT_ROOT.resolve())
    except ValueError:
        return {"ok": False,
                "error": "Attachment must live inside the project folder"}
    if any(part.startswith(".") for part in rel.parts):
        return {"ok": False,
                "error": "Hidden files/folders cannot be attached"}
    if not resolved.is_file():
        return {"ok": False, "error": "Attachment file not found"}
    if resolved.stat().st_size > MAX_ATTACHMENT_BYTES:
        return {"ok": False, "error": "Attachment exceeds 25MB"}
    return {"ok": True, "path": str(resolved)}

# ---------------------------------------------------------------------------
# Artist identity (used in signatures)
# ---------------------------------------------------------------------------

ARTIST_LINKS_SHORT = (
    "Spotify: https://open.spotify.com/artist/5k4SyH7JRPMJe1RHYMI2CT\n"
    "SoundCloud: https://soundcloud.com/inch-of-shadow\n"
    "Instagram: https://www.instagram.com/inch_of_shadow/"
)


# ---------------------------------------------------------------------------
# Personalization engine
# ---------------------------------------------------------------------------

def _display_name(contact: dict) -> str:
    """Return a clean display name for the contact.

    Uses the Discogs URL to extract a proper label name when available,
    since Discogs uses clean names like 'Dark-Entries-Records'.
    Falls back to cleaning up Instagram handles.
    """
    name = contact.get("name", "")
    # If name already has spaces or mixed case, it's a proper name
    if " " in name or (name != name.lower() and name != name.upper()):
        return name

    # Try to extract clean name from Discogs URL
    discogs_url = contact.get("discogs_url", "")
    if discogs_url and "/label/" in discogs_url:
        slug = discogs_url.split("/")[-1]
        # URL format: https://www.discogs.com/label/12345-Dark-Entries-Records
        if "-" in slug and not slug.isdigit():
            # Remove leading ID number
            label_part = slug.split("-", 1)[-1] if slug[0].isdigit() else slug
            if label_part and not label_part.isdigit():
                clean = label_part.replace("-", " ").strip()
                # Remove trailing "-2", "-3" etc (Discogs disambiguation)
                if clean and clean[-1].isdigit() and clean[-2:].startswith(" "):
                    clean = clean[:-2].strip()
                if clean:
                    return clean

    # Try Bandcamp URL: https://darkentries.bandcamp.com -> "Dark Entries"
    bandcamp = contact.get("discogs_bandcamp", "")
    if bandcamp and "bandcamp.com" in bandcamp:
        bc_slug = bandcamp.split("//")[-1].split(".")[0]
        if bc_slug and bc_slug != name.lower().replace("_", "").replace(".", ""):
            # Bandcamp slug might be cleaner
            clean = bc_slug.replace("-", " ").strip().title()
            if clean and len(clean) > 2:
                return clean

    # Fallback: clean up Instagram handle
    clean = name
    for suffix in ("_records", "records", "_official", "official", "_music",
                   "_label", "_rec", ".records", ".official"):
        if clean.lower().endswith(suffix):
            clean = clean[:len(clean) - len(suffix)]
            break
    clean = clean.replace("_", " ").replace(".", " ").strip()
    if clean:
        return clean.title()
    return name


def _clean_case(name: str) -> str:
    """Fix all-caps names to title case. Leave mixed case alone."""
    if name == name.upper() and len(name) > 3:
        # Preserve known acronyms
        words = name.split()
        result = []
        acronyms = {"EBM", "IDM", "DJ", "UK", "USA", "CPU", "DKA", "FFRR"}
        for w in words:
            if w.upper() in acronyms:
                result.append(w.upper())
            else:
                result.append(w.title())
        return " ".join(result)
    return name


def _build_greeting(contact: dict) -> str:
    """Build an official greeting."""
    label_name = _clean_case(_display_name(contact))
    return f"Dear {label_name},"


def _build_polite_opener() -> str:
    """Polite opening line."""
    return "Hope you're doing well."


def _build_personal_hook(contact: dict, release_meta: dict,
                         personal_note: str = "") -> str:
    """Build the personal context paragraph.

    Uses personal_note from user input first.
    Falls back to SI-derived context about the label/contact.
    Mentions boss name in body text if known.
    """
    if personal_note and personal_note.strip():
        return personal_note.strip()

    # Auto-generate from SI data
    boss = contact.get("label_boss", "")
    category = contact.get("category", "")
    contact_name = _clean_case(_display_name(contact))

    if category == "label":
        if boss:
            return (
                f"I've been following {contact_name} and {boss}'s work "
                f"for a while, and it really connects with the direction "
                f"I'm taking."
            )
        else:
            return (
                f"I've been following {contact_name} for a while and the "
                f"catalog really resonates with where I'm headed musically."
            )
    elif category == "media":
        return (
            f"I've been reading {contact_name} and really appreciate "
            f"how you cover the underground scene."
        )
    elif category == "venue":
        return (
            f"I've been to {contact_name} several times and it's "
            f"exactly the kind of space where my music belongs."
        )
    elif category == "promoter":
        return (
            f"I've been following {contact_name}'s events and "
            f"the lineups really resonate with my sound."
        )
    else:
        return f"I've been following your work for a while."


def _build_artist_intro(release_meta: dict) -> str:
    """One-line artist introduction. Tight and purposeful."""
    return (
        "I'm Inch of Shadow, a Berlin-based producer and DJ working with "
        "analog synths, influenced by acid, post-punk, and the darker side "
        "of disco."
    )


def _build_release_pitch(release_meta: dict, contact: dict) -> str:
    """Build the release pitch paragraph.

    No release date. Poetic sound description. No cocky genre matching.
    """
    title = release_meta.get("title", "Untitled")
    rtype = release_meta.get("release_type", "release")
    rtype = rtype if rtype.upper() == "EP" else rtype.lower()
    genre_p = release_meta.get("genre_primary", "")
    genre_s = release_meta.get("genre_secondary", "")
    genre_str = f"{genre_p} / {genre_s}" if genre_s else genre_p

    return (
        f"I've recently finished a new {rtype} called \"{title}\", "
        f"rooted in {genre_str}. The tracks were made with the "
        f"dancefloor in mind, driven by analog energy and emotional depth."
    )


def _find_genre_overlap(release_genres: str, contact_genres: str) -> str:
    """Find overlapping genre keywords between release and contact."""
    if not release_genres or not contact_genres:
        return ""

    release_set = {g.strip().lower() for g in release_genres.replace("/", ",").split(",")}
    contact_set = {g.strip().lower() for g in contact_genres.replace("/", ",").split(",")}

    overlap = release_set & contact_set
    if overlap:
        # Return the most specific match (longest name)
        best = sorted(overlap, key=len, reverse=True)[0]
        # Preserve known acronyms
        acronyms = {"ebm", "idm"}
        if best in acronyms:
            return best.upper()
        return best.title()
    return ""


def _build_link_block(private_link: str = "", listen_link: str = "") -> str:
    """Build the link section, clean and scannable."""
    if private_link:
        return private_link
    elif listen_link:
        return listen_link
    return "[add private SoundCloud link]"


def _build_call_to_action(template_id: str, contact: dict) -> str:
    """Build a subtle, respectful call to action."""
    if template_id == "label_pre":
        return (
            "I've also attached a short EPK with a bio.\n"
            "\n"
            "I'd love to hear your thoughts and see if this could find "
            "a home on the label. Thank you for your time."
        )
    elif template_id == "label_post":
        return (
            "I've also attached a short EPK with a bio.\n"
            "\n"
            "I'd love to hear your thoughts and see if this could find "
            "a home on the label. Thank you for your time."
        )
    elif template_id == "media_pre":
        return (
            "Happy to provide artwork, press shots, or anything else you need. "
            "Thank you for your time."
        )
    elif template_id == "booking":
        return (
            "I've attached an EPK with more info.\n"
            "\n"
            "I'd love to discuss availability and see if there's a good fit. "
            "Thank you for your time."
        )
    elif template_id == "festival":
        return (
            "I've attached an EPK with bio, links, and technical requirements.\n"
            "\n"
            "I'd be grateful for the opportunity to perform. Thank you for "
            "considering my application."
        )
    elif template_id == "intro":
        return (
            "I'd love to connect and explore any potential collaboration. "
            "Thank you for your time."
        )
    elif template_id == "followup":
        return "Thank you for your time."
    return ""


def _build_signature(press_contact: str = "") -> str:
    """Build the email signature."""
    sig = f"Have a pleasant journey,\nAmir Miller / Inch of Shadow\n\n{ARTIST_LINKS_SHORT}"
    if press_contact:
        sig += f"\n{press_contact}"
    return sig


# ---------------------------------------------------------------------------
# Email assembly
# ---------------------------------------------------------------------------

def _compose_email(template_id: str, release: dict, contact: dict,
                   private_link: str = "", press_contact: str = "",
                   personal_note: str = "") -> dict:
    """Assemble a complete email from personalized blocks.

    Structure:
      greeting -> polite opener -> intro -> hook -> pitch -> link -> cta -> signature
    """
    meta = release.get("metadata", {})

    # Use promo_link (secret) if set, otherwise fall back to public platform links
    if not private_link:
        private_link = release.get("promo_link", "")

    # Best public listen link (prefer SoundCloud)
    plinks = release.get("platform_links", {})
    listen_link = (
        plinks.get("soundcloud") or plinks.get("spotify") or
        plinks.get("beatport") or plinks.get("apple_music") or ""
    )

    # Build blocks
    greeting = _build_greeting(contact)
    opener = _build_polite_opener()
    intro = _build_artist_intro(meta)
    hook = _build_personal_hook(contact, meta, personal_note)
    pitch = _build_release_pitch(meta, contact)
    link = _build_link_block(private_link, listen_link)
    cta = _build_call_to_action(template_id, contact)
    signature = _build_signature(press_contact)

    title = meta.get("title", "Untitled")
    rtype = meta.get("release_type", "release")
    rtype = rtype if rtype.upper() == "EP" else rtype.lower()
    genre_p = meta.get("genre_primary", "")
    genre_s = meta.get("genre_secondary", "")
    genre_str = f"{genre_p} / {genre_s}" if genre_s else genre_p

    # -- Assemble based on template type --

    if template_id in ("label_pre", "label_post"):
        body_parts = [
            greeting,
            opener,
            "",
            intro,
            "",
            hook,
            "",
            pitch,
            "",
        ]
        if link:
            body_parts.extend([f"Here's a link to the {rtype}:", link, ""])
        body_parts.extend([cta, "", signature])
        subject = f"Demo Submission – Inch of Shadow / Berlin / {genre_str}"

    elif template_id == "media_pre":
        body_parts = [
            greeting,
            opener,
            "",
            intro,
            "",
            hook,
            "",
            pitch,
            "",
        ]
        if link:
            body_parts.extend([f"Here's a link:", link, ""])
        body_parts.extend([cta, "", signature])
        subject = f"Premiere, Inch of Shadow \"{title}\""

    elif template_id == "booking":
        body_parts = [
            greeting,
            opener,
            "",
            intro,
            "",
            hook,
            "",
            "I perform both DJ sets and live hardware performances, "
            "bringing analog synths and drum machines to the stage. "
            "My sound moves between dark disco, acid, and EBM -- "
            "built for the dancefloor with an edge.",
            "",
        ]
        if listen_link or private_link:
            body_parts.extend(["Here's a link to my music:", private_link or listen_link, ""])
        body_parts.extend([cta, "", signature])
        contact_name = _clean_case(_display_name(contact))
        subject = f"Booking Inquiry -- Inch of Shadow / Berlin"

    elif template_id == "festival":
        body_parts = [
            greeting,
            opener,
            "",
            intro,
            "",
            hook,
            "",
            "I'm reaching out to submit my application for an upcoming "
            "edition. I perform both DJ sets and live hardware shows, "
            "drawing from dark disco, acid, and EBM. My sets are "
            "high-energy, analog-driven, and built for late-night stages.",
            "",
        ]
        if listen_link or private_link:
            body_parts.extend(["Here's a link to my music:", private_link or listen_link, ""])
        body_parts.extend([cta, "", signature])
        subject = "Festival Application -- Inch of Shadow / Berlin"

    elif template_id == "intro":
        body_parts = [
            greeting,
            opener,
            "",
            intro,
            "",
            hook,
            "",
            "I'm reaching out to introduce myself and my music. "
            "I've been active in the Berlin scene, performing regularly "
            "and releasing on various platforms.",
            "",
        ]
        if listen_link or private_link:
            body_parts.extend(["Here's a link:", private_link or listen_link, ""])
        body_parts.extend([cta, "", signature])
        contact_name = _clean_case(_display_name(contact))
        subject = "Introduction -- Inch of Shadow / Berlin"

    elif template_id == "followup":
        link_line = private_link or listen_link or "[link]"
        body_parts = [
            greeting,
            "",
            f"Circling back on \"{title}\", just making sure it "
            f"didn't slip through." if title else
            "Circling back on my previous message, just making sure "
            "it didn't slip through.",
            "",
            link_line,
            "",
            cta,
            "",
            "Amir Miller / Inch of Shadow",
        ]
        subject = f"Re: {title}" if title else "Following up -- Inch of Shadow"

    else:
        return {"error": f"Unknown template: {template_id}"}

    body = "\n".join(body_parts)
    return {"subject": subject, "body": body}


# ---------------------------------------------------------------------------
# Public API (backward compatible)
# ---------------------------------------------------------------------------

def get_template_list() -> list[dict]:
    """Return list of available templates with id and display name."""
    templates = {
        "label_pre": "Label Demo (pre-release)",
        "label_post": "Label Outreach (post-release)",
        "media_pre": "Media/Premiere Pitch",
        "booking": "Booking Request",
        "festival": "Festival Submission",
        "intro": "General Introduction",
        "followup": "Follow-up",
    }
    return [{"id": k, "name": v} for k, v in templates.items()]


def render_template(template_id: str, release: dict,
                    contact_name: str = "",
                    private_link: str = "",
                    press_contact: str = "",
                    personal_note: str = "",
                    contact: dict | None = None) -> dict:
    """Render an email template with release + contact data.

    If contact dict (full SI data) is provided, uses the intelligent
    composer. Otherwise falls back to basic rendering.

    Returns {"subject": str, "body": str} or {"error": str}.
    """
    if contact is None:
        contact = {"name": contact_name, "category": "label"}

    return _compose_email(
        template_id, release, contact,
        private_link=private_link,
        press_contact=press_contact,
        personal_note=personal_note,
    )


def auto_select_template(category: str, release_date: str) -> str:
    """Pick the best template based on contact category and release timing."""
    # General outreach (no release date) -- pick by category
    if not release_date:
        if category == "venue" or category == "promoter":
            return "booking"
        if category == "media":
            return "intro"
        return "intro"

    is_pre = False
    try:
        rd = datetime.strptime(release_date, "%Y-%m-%d")
        is_pre = rd > datetime.now()
    except ValueError:
        pass

    if category == "media":
        return "media_pre"
    if category in ("venue", "promoter"):
        return "booking"
    return "label_pre" if is_pre else "label_post"


# ---------------------------------------------------------------------------
# SMTP sending
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def can_send() -> dict:
    """Check if we can send right now. Rate state is persistent — a webapp
    restart no longer resets the hourly budget (audit P4-24)."""
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        return {"ok": False, "reason": "Gmail credentials not configured in .env",
                "sent_this_hour": 0}

    now = time.time()
    cutoff = now - 3600
    recent = sorted(s.get("ts", 0) for s in _load_send_state()
                    if isinstance(s, dict) and s.get("ts", 0) > cutoff)

    if len(recent) >= MAX_PER_HOUR:
        return {"ok": False, "reason": f"Rate limit reached ({MAX_PER_HOUR}/hour)",
                "sent_this_hour": len(recent)}

    if recent and (now - recent[-1]) < MIN_INTERVAL_SEC:
        return {"ok": False, "reason": "Too fast -- wait a few seconds",
                "sent_this_hour": len(recent)}

    return {"ok": True, "reason": "", "sent_this_hour": len(recent)}


def send_email(to_addr: str, subject: str, body: str,
               attachment_path: str = "", force: bool = False) -> dict:
    """Send a plain text email via Gmail SMTP, optionally with a file attachment.

    Hardened per audit P4-24: header-injection rejection, attachment path
    restriction, verified TLS, persistent rate state, duplicate-send guard
    (same recipient + subject within 24h refused unless force=True).
    """
    if not _EMAIL_RE.match(to_addr):
        return {"ok": False, "error": "Invalid email address"}
    if _header_injection(subject):
        return {"ok": False, "error": "Subject contains line breaks (header injection)"}

    # Duplicate guard first — it's the more specific refusal than "too fast".
    if not force:
        dup = find_recent_duplicate(to_addr, subject)
        if dup:
            when = datetime.fromtimestamp(dup["ts"]).strftime("%Y-%m-%d %H:%M")
            return {"ok": False, "duplicate": True,
                    "error": f"Already sent to {to_addr} with this subject at "
                             f"{when}. Pass force=True to resend."}

    status = can_send()
    if not status["ok"]:
        return {"ok": False, "error": status["reason"]}

    # Build message -- multipart if attachment, plain text otherwise
    if attachment_path:
        checked = validate_attachment(attachment_path)
        if not checked["ok"]:
            return {"ok": False, "error": checked["error"]}
        attachment_path = checked["path"]

        msg = MIMEMultipart()
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Attach file
        filename = os.path.basename(attachment_path)
        ctype, _ = mimetypes.guess_type(attachment_path)
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        with open(attachment_path, "rb") as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(part)
    else:
        msg = MIMEText(body, "plain", "utf-8")

    msg["From"] = formataddr((SENDER_NAME, GMAIL_ADDRESS))
    msg["To"] = to_addr
    msg["Subject"] = subject

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.starttls(context=ssl.create_default_context())
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, [to_addr], msg.as_string())
        server.quit()
        _record_send(to_addr, subject)
        return {"ok": True, "error": ""}
    except (smtplib.SMTPException, ssl.SSLError, OSError) as exc:
        return {"ok": False, "error": str(exc)}
