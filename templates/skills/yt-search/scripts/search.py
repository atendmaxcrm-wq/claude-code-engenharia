#!/usr/bin/env python3
"""YouTube search with dual backend: yt-dlp (primary) or HTTP scraping (fallback)."""

import io
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def parse_args(argv):
    args = argv[1:]
    count = 20
    months = 6
    query_parts = []
    i = 0
    while i < len(args):
        if args[i] == "--count" and i + 1 < len(args):
            try:
                count = int(args[i + 1])
            except ValueError:
                print(f"Error: --count requires an integer, got '{args[i + 1]}'", file=sys.stderr)
                sys.exit(1)
            i += 2
        elif args[i] == "--months" and i + 1 < len(args):
            try:
                months = int(args[i + 1])
            except ValueError:
                print(f"Error: --months requires an integer, got '{args[i + 1]}'", file=sys.stderr)
                sys.exit(1)
            i += 2
        elif args[i] == "--no-date-filter":
            months = 0
            i += 1
        else:
            query_parts.append(args[i])
            i += 1
    query = " ".join(query_parts)
    if not query:
        print("Usage: search.py <query> [--count N] [--months N] [--no-date-filter]", file=sys.stderr)
        print("Example: search.py claude code tutorial --count 5 --months 3", file=sys.stderr)
        sys.exit(1)
    return query, count, months


def format_subscribers(n):
    if n is None:
        return "N/A"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def format_views(n):
    if n is None:
        return "N/A"
    return f"{n:,}"


def format_duration_secs(dur):
    if dur is None:
        return "N/A"
    dur = int(dur)
    hours, remainder = divmod(dur, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def format_duration(info):
    if info.get("duration_string"):
        return info["duration_string"]
    dur = info.get("duration")
    return format_duration_secs(dur)


def format_date(raw):
    if not raw or len(raw) != 8:
        return "N/A"
    try:
        dt = datetime.strptime(raw, "%Y%m%d")
        return dt.strftime("%b %d, %Y")
    except ValueError:
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"


def get_cutoff_date(months):
    if months <= 0:
        return None
    cutoff = datetime.now() - timedelta(days=months * 30)
    return cutoff.strftime("%Y%m%d")


def parse_view_count(text):
    """Parse view count from strings like '1.2M views', '450K views', '12,345 views'."""
    if not text:
        return None
    text = text.lower().replace(",", "").replace(".", "")
    m = re.search(r'([\d.]+)\s*m', text)
    if m:
        return int(float(m.group(1)) * 1_000_000)
    m = re.search(r'([\d.]+)\s*k', text)
    if m:
        return int(float(m.group(1)) * 1_000)
    m = re.search(r'(\d+)', text)
    if m:
        return int(m.group(1))
    return None


def parse_relative_date(text):
    """Parse relative dates like '2 months ago', '3 weeks ago' to YYYYMMDD."""
    if not text:
        return None
    text = text.lower().strip()
    now = datetime.now()
    m = re.search(r'(\d+)\s*(hour|day|week|month|year)s?\s*ago', text)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2)
    if unit == "hour":
        dt = now - timedelta(hours=n)
    elif unit == "day":
        dt = now - timedelta(days=n)
    elif unit == "week":
        dt = now - timedelta(weeks=n)
    elif unit == "month":
        dt = now - timedelta(days=n * 30)
    elif unit == "year":
        dt = now - timedelta(days=n * 365)
    else:
        return None
    return dt.strftime("%Y%m%d")


def search_ytdlp(query, fetch_count):
    """Try yt-dlp search (rich metadata, needs auth sometimes)."""
    if not shutil.which("yt-dlp"):
        return None
    search_query = f"ytsearch{fetch_count}:{query}"
    cmd = [
        "yt-dlp", search_query,
        "--dump-json", "--no-download", "--no-warnings", "--quiet",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    if result.returncode != 0 and not result.stdout.strip():
        return None
    videos = []
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        try:
            videos.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return videos if videos else None


def search_http_scrape(query, fetch_count):
    """Fallback: scrape YouTube search results page (no auth needed)."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"HTTP scrape failed: {e}", file=sys.stderr)
        return None

    # Extract ytInitialData JSON from page
    m = re.search(r'var ytInitialData\s*=\s*(\{.+?\});\s*</script>', html, re.DOTALL)
    if not m:
        m = re.search(r'ytInitialData\s*=\s*(\{.+?\});\s*', html, re.DOTALL)
    if not m:
        print("Could not extract ytInitialData from page.", file=sys.stderr)
        return None

    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        print("Failed to parse ytInitialData JSON.", file=sys.stderr)
        return None

    videos = []
    try:
        contents = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]
        for section in contents:
            items = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                vr = item.get("videoRenderer")
                if not vr:
                    continue
                video_id = vr.get("videoId", "")
                title_runs = vr.get("title", {}).get("runs", [])
                title = "".join(r.get("text", "") for r in title_runs)
                channel_runs = vr.get("ownerText", {}).get("runs", [])
                channel = "".join(r.get("text", "") for r in channel_runs)
                view_text = vr.get("viewCountText", {}).get("simpleText", "")
                if not view_text:
                    view_text = "".join(r.get("text", "") for r in vr.get("viewCountText", {}).get("runs", []))
                views = parse_view_count(view_text)
                duration_text = vr.get("lengthText", {}).get("simpleText", "")
                published_text = vr.get("publishedTimeText", {}).get("simpleText", "")
                upload_date = parse_relative_date(published_text)

                # Parse duration to seconds
                dur_secs = None
                if duration_text:
                    parts = duration_text.split(":")
                    try:
                        if len(parts) == 3:
                            dur_secs = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        elif len(parts) == 2:
                            dur_secs = int(parts[0]) * 60 + int(parts[1])
                    except ValueError:
                        pass

                videos.append({
                    "id": video_id,
                    "title": title,
                    "channel": channel,
                    "view_count": views,
                    "channel_follower_count": None,
                    "duration": dur_secs,
                    "duration_string": duration_text,
                    "upload_date": upload_date,
                    "published_text": published_text,
                })
                if len(videos) >= fetch_count:
                    break
    except (KeyError, TypeError) as e:
        print(f"Error parsing search results: {e}", file=sys.stderr)
        return None

    return videos if videos else None


def display_results(videos, count, months):
    cutoff = get_cutoff_date(months)
    if cutoff:
        filtered = [v for v in videos if (v.get("upload_date") or "00000000") >= cutoff]
        skipped = len(videos) - len(filtered)
        videos = filtered
        if skipped > 0:
            print(f"(Filtered out {skipped} video(s) older than {months} months)\n", file=sys.stderr)

    if not videos:
        print(f"No results found within the last {months} months.", file=sys.stderr)
        sys.exit(0)

    videos = videos[:count]
    divider = "\u2500" * 60

    for i, info in enumerate(videos, 1):
        title = info.get("title", "Unknown Title")
        channel = info.get("channel", info.get("uploader", "Unknown"))
        views = info.get("view_count")
        subs = info.get("channel_follower_count")
        duration = format_duration(info)
        date = format_date(info.get("upload_date", ""))
        published = info.get("published_text", "")
        video_id = info.get("id", "")
        url = f"https://youtube.com/watch?v={video_id}" if video_id else "N/A"

        if subs and views and subs > 0:
            ratio = views / subs
            ratio_str = f"{ratio:.2f}x"
        else:
            ratio_str = "N/A"

        views_str = format_views(views)
        subs_str = format_subscribers(subs)
        date_display = date if date != "N/A" else published
        meta = f"{channel} ({subs_str} subs)  \u00b7  {views_str} views  \u00b7  {duration}  \u00b7  {date_display}"

        print(divider)
        print(f" {i:>2}. {title}")
        print(f"     {meta}")
        print(f"     {url}")

    print(divider)


def main():
    query, count, months = parse_args(sys.argv)
    fetch_count = count * 2 if months > 0 else count
    date_label = f", last {months} months" if months > 0 else ""
    print(f"Searching YouTube for: \"{query}\" (top {count} results{date_label})...\n", file=sys.stderr)

    # Try yt-dlp first (richer metadata)
    videos = search_ytdlp(query, fetch_count)
    if videos:
        print("(via yt-dlp)\n", file=sys.stderr)
        display_results(videos, count, months)
        return

    # Fallback to HTTP scraping
    print("(yt-dlp unavailable or blocked, using HTTP scrape fallback)\n", file=sys.stderr)
    videos = search_http_scrape(query, fetch_count)
    if videos:
        display_results(videos, count, months)
        return

    print("No results found with any backend.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
