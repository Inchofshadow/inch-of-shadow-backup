# Inch of Shadow code backup

Snapshot of the Inchofshadowcode folder, no git history from the Mac repo.
Built by plans/cleanup/backup_snapshot.py. The Mac copy is the original; this is an extra copy.

- Plain files: readable as they are.
- `*.enc` files: hold other people's contact data or IG exports. Encrypted with
  openssl aes-256-cbc + pbkdf2 (200000 rounds). The key is only on the Mac and on the Intenso drive.
  Decrypt one: `openssl enc -d -aes-256-cbc -md sha256 -pbkdf2 -iter 200000 -pass file:KEY -in X.enc -out X`
- Not in here: secrets (.env, tokens, OAuth files, login cookies), private DM messages, big media.
