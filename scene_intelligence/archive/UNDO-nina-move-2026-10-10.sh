#!/bin/sh
# Undo the 2026-10-10 archive move (ticket M-04)
cd "$(dirname "$0")/.." && mv archive/nina_follow_log.json archive/nina_hub_stats.json . && echo restored
