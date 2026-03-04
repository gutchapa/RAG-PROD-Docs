#!/usr/bin/env python3
"""Chennai Drik Panchangam - Complete Details with Eclipse Info"""

import requests
import re
from datetime import datetime

def get_chennai_panchang():
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    
    url = f"https://www.drikpanchang.com/panchang/day-panchang.html?city=chennai&date={date_str}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        text = response.text
        
        # Remove HTML tags for easier parsing
        text_clean = re.sub(r'<[^>]+>', ' ', text)
        text_clean = re.sub(r'\s+', ' ', text_clean)
        
        print(f"🌅 Chennai Drik Panchangam")
        print(f"📅 {today.strftime('%A, %d %B %Y')}")
        print("")
        
        # === DATE & TITHI INFO ===
        print("📿 Panchang Details")
        print("─" * 30)
        
        # Extract date info
        date_match = re.search(r'(\w+day),?\s*(\w+)\s*Paksha,\s*(\w+)', text_clean)
        if date_match:
            print(f"• Day: {date_match.group(1)}")
            print(f"• Paksha: {date_match.group(2)} Paksha")
            print(f"• Tithi: {date_match.group(3)}")
        
        # Nakshatra
        nakshatra_match = re.search(r'Nakshatra\s+([A-Za-z]+)\s+upto', text_clean)
        if nakshatra_match:
            nakshatra_name = nakshatra_match.group(1)
            if len(nakshatra_name) > 2:
                print(f"• Nakshatra: {nakshatra_name}")
        
        # Yoga
        yoga_match = re.search(r'Yoga\s+([A-Za-z]+)(?=\s+upto|\s+Karana|$)', text_clean)
        if yoga_match:
            yoga_name = yoga_match.group(1)
            if len(yoga_name) > 2 and yoga_name not in ['and', 'The']:
                print(f"• Yoga: {yoga_name}")
        
        # Karana
        karana_match = re.search(r'Karana\s+([A-Za-z]+)(?=\s+upto|\s+Sunrise|$)', text_clean)
        if karana_match:
            karana_name = karana_match.group(1)
            if len(karana_name) > 2:
                print(f"• Karana: {karana_name}")
        
        # Samvatsara
        samvat_match = re.search(r'Samvatsara\s+(\w+)', text_clean)
        if samvat_match:
            print(f"• Samvatsara: {samvat_match.group(1)}")
        
        print("")
        
        # === SUN/MOON TIMINGS ===
        print("☀️🌙 Celestial Timings")
        print("─" * 30)
        
        sun_patterns = [
            (r'Sunrise\s+(\d+:\d+)\s*(AM|PM)', 'Sunrise ☀️'),
            (r'Sunset\s+(\d+:\d+)\s*(AM|PM)', 'Sunset 🌅'),
            (r'Moonrise\s+(\d+:\d+)\s*(AM|PM)', 'Moonrise 🌙'),
            (r'Moonset\s+(\d+:\d+)\s*(AM|PM)', 'Moonset 🌑'),
        ]
        
        for pattern, name in sun_patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                time_str = f"{match.group(1)} {match.group(2)}"
                print(f"• {name}: {time_str}")
        
        print("")
        
        # === AUSPICIOUS/INAUSPICIOUS TIMINGS ===
        print("⏰ Muhurta Timings")
        print("─" * 30)
        
        patterns = [
            (r'Brahma Muhurta\s+(\d+:\d+)\s*(AM|PM)\s*to\s*(\d+:\d+)\s*(AM|PM)', '🙏 Brahma Muhurta'),
            (r'Pratah Sandhya\s+(\d+:\d+)\s*(AM|PM)\s*to\s*(\d+:\d+)\s*(AM|PM)', 'Pratah Sandhya'),
            (r'Abhijit\s+(\d+:\d+)\s*(AM|PM)\s*to\s*(\d+:\d+)\s*(AM|PM)', '⭐ Abhijit Muhurta'),
            (r'Vijaya Muhurta\s+(\d+:\d+)\s*(AM|PM)\s*to\s*(\d+:\d+)\s*(AM|PM)', '⭐ Vijaya Muhurta'),
            (r'Rahu Kalam\s+(\d+:\d+)\s*(AM|PM)\s*to\s*(\d+:\d+)\s*(AM|PM)', '⚠️ Rahu Kalam (avoid)'),
            (r'Gulika Kalam\s+(\d+:\d+)\s*(AM|PM)\s*to\s*(\d+:\d+)\s*(AM|PM)', '⚠️ Gulika Kalam (avoid)'),
            (r'Yamaganda\s+(?:Kalam\s+)?(\d+:\d+)\s*(AM|PM)\s*to\s*(\d+:\d+)\s*(AM|PM)', '⚠️ Yamaganda (avoid)'),
        ]
        
        for pattern, name in patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                time_str = f"{match.group(1)} {match.group(2)} to {match.group(3)} {match.group(4)}"
                print(f"• {name}: {time_str}")
        
        # Check for Abhijit None
        if re.search(r'Abhijit\s+(?:Muhurta\s+)?None', text_clean, re.IGNORECASE):
            print("• ⭐ Abhijit Muhurta: None today")
        
        print("")
        
        # === ECLIPSE DETAILS ===
        print("🌑 Eclipse Information")
        print("─" * 30)
        
        # More specific eclipse detection - look for "Eclipse" near date or with specific patterns
        # Check if there's an actual eclipse section (not just navigation links)
        
        # Look for eclipse warnings/alerts in the content
        eclipse_alert = re.search(r'(Surya Grahan|Chandra Grahan|Solar Eclipse|Lunar Eclipse).*?(\d{1,2}:\d{2}\s*(?:AM|PM)).*?(\d{1,2}:\d{2}\s*(?:AM|PM))', text_clean, re.IGNORECASE)
        
        # Also check raw HTML for eclipse indicators
        has_eclipse_section = 'eclipse' in text.lower() and ('grahan' in text.lower() or 'solar eclipse today' in text.lower() or 'lunar eclipse today' in text.lower())
        
        # Check for eclipse in main content (exclude navigation)
        # Look for "Eclipse" followed by specific timing info within reasonable distance
        eclipse_in_content = False
        eclipse_type = None
        eclipse_start = None
        eclipse_end = None
        
        for match in re.finditer(r'(Surya Grahan|Chandra Grahan|Solar Eclipse|Lunar Eclipse)', text_clean, re.IGNORECASE):
            # Get context around the match
            start = max(0, match.start() - 100)
            end = min(len(text_clean), match.end() + 200)
            context = text_clean[start:end]
            
            # Check if this context has timing info and not just navigation
            if re.search(r'\d{1,2}:\d{2}\s*(?:AM|PM)', context) and 'calendar' not in context.lower():
                eclipse_in_content = True
                eclipse_type = match.group(1).title()
                
                # Extract times from this context
                times = re.findall(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', context)
                if len(times) >= 2:
                    eclipse_start = times[0]
                    eclipse_end = times[1]
                elif len(times) == 1:
                    eclipse_start = times[0]
                break
        
        if eclipse_in_content and eclipse_type:
            print(f"⚠️ {eclipse_type} Today!")
            if eclipse_start:
                print(f"   Start: {eclipse_start}")
            if eclipse_end:
                print(f"   End: {eclipse_end}")
            
            # Check Chennai visibility
            if 'chennai' in text_clean.lower() or 'india' in text_clean.lower():
                print(f"   ✓ Visible in Chennai/India")
            else:
                print(f"   Check drikpanchang.com for visibility")
        else:
            print("✅ No eclipse (Grahan) today")
        
        # Show next eclipse if available
        next_eclipse = re.search(r'next\s+(solar|lunar).*?eclipse.*?(\d{1,2}\s+\w+)', text_clean, re.IGNORECASE)
        if next_eclipse:
            print(f"📅 Next {next_eclipse.group(1).title()} Eclipse: {next_eclipse.group(2)}")
        
        print("")
        print("🙏 Source: drikpanchang.com")
        print("📝 Note: All timings are for Chennai, IST")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_chennai_panchang()
