#!/usr/bin/env python3
"""Helper functions for IG enrichment - called from main enrichment loop."""
import json
import re
from datetime import datetime, timezone


def parse_number(text):
    text = text.replace(',', '').strip()
    if text.upper().endswith('K'):
        return int(float(text[:-1]) * 1000)
    if text.upper().endswith('M'):
        return int(float(text[:-1]) * 1000000)
    try:
        return int(text)
    except Exception:
        return 0


def parse_ig_page(page_text, handle):
    result = {
        'ig_handle_checked': handle,
        'ig_enriched_at': datetime.now(timezone.utc).isoformat()
    }
    if not page_text:
        result['ig_parse_error'] = 'empty'
        return result
    t = page_text.replace('\n', ' ')
    if 'This Account is Private' in t or 'account is private' in t.lower():
        result['ig_is_private'] = True
        result['ig_followers'] = 0
        return result
    if "Sorry, this page isn't available" in t or 'Page Not Found' in t:
        result['ig_not_found'] = True
        return result
    m = re.search(r'([\d,\.]+[KkMm]?)\s*followers', t)
    if m:
        result['ig_followers'] = parse_number(m.group(1))
    m = re.search(r'([\d,\.]+[KkMm]?)\s*following', t)
    if m:
        result['ig_following'] = parse_number(m.group(1))
    m = re.search(r'([\d,\.]+[KkMm]?)\s*posts', t)
    if m:
        result['ig_posts'] = parse_number(m.group(1))
    result['ig_is_verified'] = bool(re.search(r'verified', t, re.IGNORECASE)) if 'followers' in t else False
    result['ig_is_private'] = False
    bio_match = re.search(r'\d+\s*following(.{5,300}?)(?:Edit profile|Follow|Message|Link icon|Highlights|Posts)', t)
    if bio_match:
        bio = bio_match.group(1).strip()[:200]
        result['ig_bio'] = bio
    return result


def save_results(results_dict, processed_count, total, enriched_contacts_path, results_path):
    """Save results to enriched_contacts.json and progress file."""
    with open(enriched_contacts_path) as f:
        contacts = json.load(f)

    for handle, result in results_dict.items():
        idx = result.get('_index')
        if idx is not None and idx < len(contacts):
            for k, v in result.items():
                if k != '_index':
                    contacts[idx][k] = v

    with open(enriched_contacts_path, 'w') as f:
        json.dump(contacts, f, indent=2)

    # Save progress file
    progress = {
        'processed': processed_count,
        'total': total,
        'results': {h: {k: v for k, v in r.items() if k != '_index'} for h, r in results_dict.items()}
    }
    with open(results_path, 'w') as f:
        json.dump(progress, f, indent=2)

    return len(contacts)


if __name__ == '__main__':
    # Test parse
    sample = "mannequinrecordsOptionsMannequin Records1,585 posts20K followers2,027 followingRecord label"
    r = parse_ig_page(sample, 'mannequinrecords')
    print(r)
