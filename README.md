# ANYWHERE 2027
Modern flight-deal tracker V1 prototype.

## Current V1
- Anywhere-style search UI
- Today's best deals
- 2027 monthly price overview
- Watchlist
- Auto-update schedule display at 12:00 Thailand time
- Manual "UPDATE NOW" interaction
- Responsive desktop/mobile design

## Next integration
Connect the frontend to Supabase and a permitted flight-fare data source/API. Store fare snapshots with timestamps, source, route, baggage assumptions, and booking URL. Then run a scheduled job daily at 12:00 Asia/Bangkok and allow manual refresh with rate limiting.
