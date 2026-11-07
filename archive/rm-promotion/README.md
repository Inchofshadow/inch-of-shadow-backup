What: the Promotion page's email module (email_outreach.py), the contact scoring used by the Engagement and Promotion pages (contact_bridge.py) and the email module's tests, moved out of release_manager/ and tests/.
Why: RM 2.0 slice 1 (2026-11-06, Amir: "Yes, all 5") dropped the Promotion and Engagement pages; nothing else imports these files, and no email was ever sent.
Undo: git mv each file back (the two modules to release_manager/, the test to tests/) and restore the routes from the commit before "RM 2.0 slice 1a".
