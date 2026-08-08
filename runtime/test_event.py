from playlist_bridge.domain import events

e = events.MatchProgressEvent(
    job_id='test',
    total_tracks=10,
    matched_count=5,
    reviewed_count=2,
    skipped_count=1,
    timestamp='2026-08-07T01:00:51.671Z'
)
assert e.type == 'match_progress'
print('Event verified')
print(f'type={e.type}')
print(f'job_id={e.job_id}')
