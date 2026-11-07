"""
stats/
------
Tool 5 -- Stats Dashboard: platform stats collection, storage, and analysis.

Collects follower counts, play counts, and engagement metrics from:
  - Spotify (Client Credentials API)
  - SoundCloud (OAuth user token)
  - YouTube (Data API v3)
  - Instagram (Meta Graph API)
  - Bandcamp, Beatport, Apple Music (manual entry -- no public APIs)

Data stored as JSON snapshots in stats_snapshots/.
"""
