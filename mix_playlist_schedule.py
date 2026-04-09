#!/usr/bin/env python3
import sqlite3
import argparse
from datetime import datetime, timedelta
import os

# Default DB locations
DB_MAC = os.path.expanduser(
    "~/Library/Containers/org.mixxx.mixxx/data/Library/Application Support/mixxx/mixxxdb.sqlite"
)
DB_LINUX = os.path.expanduser("~/.mixxx/mixxxdb.sqlite")

def parse_args():
    parser = argparse.ArgumentParser(description="Estimate AutoDJ track start times.")
    parser.add_argument("-d", "--db", default=None, help="Path to Mixxx database")
    parser.add_argument("-t", "--start", default=None,
                        help="AutoDJ start time. Formats: HH, HH:MM, YYYY-MM-DD HH:MM")
    parser.add_argument("-p", "--playlist", default="Auto DJ", help="Playlist name")
    parser.add_argument("-c", "--crossfade", type=int, default=0,
                        help="Crossfade in seconds between tracks")
    parser.add_argument("--round-minutes", type=int, default=5,
                        help="Round start time to nearest N minutes (default 5)")
    parser.add_argument("--hide-hour-labels", action="store_true",
                        help="Hide 'Second Hour', 'Third Hour', etc.")
    return parser.parse_args()

def detect_db(provided_db):
    if provided_db:
        db = provided_db
    elif os.path.exists(DB_MAC):
        db = DB_MAC
    elif os.path.exists(DB_LINUX):
        db = DB_LINUX
    else:
        raise FileNotFoundError("Mixxx database not found.")
    return db

def round_time(dt, minutes=5):
    # Round up to next N minutes
    discard = timedelta(minutes=dt.minute % minutes,
                        seconds=dt.second,
                        microseconds=dt.microsecond)
    dt += timedelta(minutes=minutes) - discard
    return dt.replace(second=0, microsecond=0)

def parse_start_time(start_str, round_minutes=5):
    now = datetime.now()
    if not start_str:
        return round_time(now, round_minutes)
    try:
        if len(start_str) <= 2:  # hour only
            dt = datetime(now.year, now.month, now.day, int(start_str), 0)
        elif len(start_str) <= 5:  # HH:MM
            hour, minute = map(int, start_str.split(":"))
            dt = datetime(now.year, now.month, now.day, hour, minute)
        else:  # full date-time
            dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
    except Exception:
        raise ValueError("Invalid start time format.")
    return dt

def fetch_tracks(db_path, playlist_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Playlists WHERE name=?", (playlist_name,))
    if cursor.fetchone()[0] == 0:
        raise ValueError(f"Playlist '{playlist_name}' does not exist.")

    query = """
    SELECT pt.position,
           COALESCE(l.title,''),
           COALESCE(l.duration,0),
           COALESCE(l.comment,''),
           COALESCE(l.artist,'')
    FROM PlaylistTracks pt
    JOIN Playlists p ON pt.playlist_id = p.id
    JOIN library l ON l.id = pt.track_id
    WHERE p.name=?
    ORDER BY pt.position ASC;
    """
    cursor.execute(query, (playlist_name,))
    tracks = cursor.fetchall()
    conn.close()
    return tracks

def format_length(seconds):
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    return f"{minutes}:{sec:02d}"

def main():
    args = parse_args()
    db = detect_db(args.db)
    start_dt = parse_start_time(args.start, args.round_minutes)
    crossfade = args.crossfade

    tracks = fetch_tracks(db, args.playlist)
    total_sec = 0
    last_hour_printed = 1

    print(f"AutoDJ Schedule for playlist: '{args.playlist}'")
    print(f"Start time: {start_dt.strftime('%H:%M')} on {start_dt.strftime('%Y-%m-%d')}")
    print(f"Crossfade: {crossfade} seconds\n")

    print("Pos | Starts | Elapsed | Length | Comment | Track Title | Artist")
    print("----|--------|--------|-------|---------|------------|-------")

    for pos, title, duration, comment, artist in tracks:
        pos = pos or 0
        title = title or "Unknown"
        duration = duration or 0
        comment = comment or "Empty"
        artist = artist or "Unknown"

        dur_sec = round(float(duration))
        start_time = start_dt + timedelta(seconds=total_sec)
        elapsed = timedelta(seconds=total_sec)
        elapsed_str = f"{elapsed.seconds//3600}:{(elapsed.seconds%3600)//60:02d}" if elapsed.seconds>=3600 else f"{(elapsed.seconds%3600)//60}:{elapsed.seconds%60:02d}"

        # Hour label (skip first hour)
        if not args.hide_hour_labels:
            cur_hour = total_sec // 3600 + 1
            if cur_hour > 1 and cur_hour != last_hour_printed:
                label = {2:"Second Hour",3:"Third Hour",4:"Fourth Hour"}.get(cur_hour,f"{cur_hour}th Hour")
                print(f"\n=== {label} ===")
                last_hour_printed = cur_hour

        print(f"{pos:02d} | {start_time.strftime('%H:%M')} | {elapsed_str} | {format_length(dur_sec)} | {comment} | {title} | {artist}")

        # Increment total seconds (apply crossfade)
        inc = dur_sec - crossfade
        if inc < 0: inc = 0
        total_sec += inc

if __name__ == "__main__":
    main()
