# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## Daily Tasks

### Chennai Drik Panchangam (Morning)
- Run: `python3 /root/.openclaw/workspace/scripts/chennai_panchang.py`
- Schedule: Daily via cron at 6:00 AM IST (12:30 AM UTC)
- Action: Send complete panchangam details to user including:
  * Tithi, Nakshatra, Yoga, Karana, Samvatsara
  * Sunrise, Sunset, Moonrise, Moonset
  * Brahma Muhurta, Abhijit Muhurta, Vijaya Muhurta
  * Rahu Kalam, Gulika Kalam, Yamaganda
  * Eclipse (Grahan) information with timings if visible in Chennai
