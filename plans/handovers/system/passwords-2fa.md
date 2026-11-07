# ⚙️ System: Passwords + 2FA (side chat), handover

Updated 2026-11-06.

## Where it stands
- ✅ Inventory built from Chrome saved-login metadata, profiles Inch of Shadow (Profile 7, 30 entries) + Amir (Default, 318 entries). Amir named these two; Gero (Profile 2, 5) and amirmill808 (Profile 3) not read.
- Method (Amir picked): local read-only SQLite (`immutable=1`), password column never selected, no browser clicks.
- 292 accounts after merging, 9 categories, Chrome leak flags ignored (Amir 11-06), 74 stale (<2024), 7 throwaway emails.
- 2FA state unknown for all rows (not in Chrome data); Amir fills it in.

## Files
- `plans/passwords-2fa/README.md` - summary, change order, 2FA policy, password manager options
- `plans/passwords-2fa/inventory.json` - per-account list (no passwords, ID/bank usernames masked)
- `plans/passwords-2fa/read_logins_meta.py`, `build_inventory.py` - rebuild, read-only

## Open decisions (Amir)
- Approve the 2FA policy per category.
- Password manager: stay on Google / Apple Passwords / 1Password-Bitwarden.
- Read Gero + amirmill808 profiles too? (only on his word)

## Ticket updates (for the ⚙️ System parent to merge)
- New: ⚙️ System, "Passwords + 2FA", bucket ⏭️ next, who 🙋 amir, chrome 🌐 true, next_step: email inboxes 2FA -> money -> release/promo; inventory in plans/passwords-2fa/.
