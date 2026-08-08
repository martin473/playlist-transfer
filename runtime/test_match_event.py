#!/usr/bin/env python
"""Test MatchProgressEvent."""

from playlist_bridge.domain import events

# Create an instance of MatchProgressEvent
e = events.MatchProgressEvent(
    job_id='test',
    total_tracks=1,
    matched_count=1,
    reviewed_count=0,
    skipped_count=0,
    timestamp='2026-08-07T01:00:51.671Z'
)

print(f'type={e.type}')
assert e.type == 'match_progress'
print('Event verified')
