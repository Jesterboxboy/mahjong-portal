# -*- coding: utf-8 -*-
"""
EMA website scraper for Austrian player results.

HTML structure of the EMA ranking site (https://mahjong-europe.org/ranking/):

  Country players page (/ranking/Country/AUT_RCR.html):
    div.TCTT_lignes > div.TCTT_ligne|TCTT_ligneG (one per player; first is header)
      p[0]: EMA global rank
      p[1]: national rank
      p[2]: EMA ID  (text of <a><u>01000148</u></a>)
      p[3]: last name (uppercase)
      p[4]: first name (uppercase)
      p[5]: country flag img
      p[6]: total EMA points
      p[7]: number of tournaments
      p[8]: win trophies

  Individual player page (/ranking/Players/{ema_id}.html):
    Players may have results in both Riichi (TR_RCR_) and MCR (TR_) rulesets.
    Only the Riichi results table is imported.  It is located by finding the
    first <h3> (or <h2>) heading whose text contains "Riichi" and then taking
    the first <table> element that follows it in the document.
    Header row: TR.HallFame_EnteteTableau — Id, Date, Place, Tournament, W, Rank, Points, ...
    Data rows:
      td[0]: tournament id (integer)
      td[1]: date range text, e.g. "18-19 April 2026"
      td[2]: country flag img + city
      td[3]: tournament name (link, href like "../Tournament/TR_RCR_409.html")
      td[4]: weight (MERS)
      td[5]: rank text "position/player_count", e.g. "15/64"
      td[6]: points text, e.g. "778 pts"
"""

import logging
import re

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as du_parse
from django.conf import settings

from austria_ranking.models import EmaTournamentResult

logger = logging.getLogger(__name__)

URLBASE = getattr(settings, "EMA_RANKING_URL", "https://mahjong-europe.org/ranking/")
COUNTRY_FLAG_PATTERN = re.compile(r"/([a-z]{2})\.png")
# Matches the end day from a date range like "18-19 April 2026" or "07-08 Mar.2026"
_DATE_END_PATTERN = re.compile(r"(?:\d+\s*[-\u2013]\s*)?(\d{1,2})\s*([A-Za-z]+)[\s.]*(\d{4})", re.IGNORECASE)


def _parse_end_date(date_text: str):
    """Extract the end date from a date-range string such as '18-19 April 2026'."""
    m = _DATE_END_PATTERN.search(date_text)
    if m:
        try:
            return du_parse(f"{m.group(1)} {m.group(2)} {m.group(3)}").date()
        except Exception:
            pass
    return None


def _get(url: str) -> BeautifulSoup:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, "html.parser")


def scrape_at_players() -> list[dict]:
    """
    Fetch the list of Austrian-registered EMA riichi players.

    Returns a list of dicts: {ema_id, first_name, last_name}
    """
    url = f"{URLBASE}Country/AUT_RCR.html"
    logger.info("Fetching AT players from %s", url)
    try:
        soup = _get(url)
    except Exception as exc:
        logger.error("Failed to fetch AT players page: %s", exc)
        return []

    players = []
    try:
        lignes = soup.find("div", class_="TCTT_lignes")
        rows = lignes.find_all("div", class_=re.compile(r"^TCTT_ligne"))
        for row in rows[1:]:  # skip header row
            p_tags = row.find_all("p")
            if len(p_tags) < 5:
                continue
            ema_id = p_tags[2].get_text(strip=True)
            if not ema_id.isdigit():
                continue
            last_name = p_tags[3].get_text(strip=True).title()
            first_name = p_tags[4].get_text(strip=True).title()
            players.append({"ema_id": ema_id, "first_name": first_name, "last_name": last_name})
    except Exception as exc:
        logger.error("Error parsing AT players page: %s", exc)

    logger.info("Found %d AT players", len(players))
    return players


def scrape_at_ranking() -> list[dict]:
    """
    Fetch the Austrian EMA RCR ranking including EMA points totals.

    Returns a list of dicts:
        {ema_id, first_name, last_name, ema_rank (int), total_points (int)}
    sorted by total_points descending (i.e. Austrian rank by total score).

    Column indices inside each .TCTT_ligne row (per the HTML structure above):
      p[0]: EMA global rank
      p[2]: EMA ID
      p[3]: last name
      p[4]: first name
      p[6]: total EMA points
    """
    url = f"{URLBASE}Country/AUT_RCR.html"
    logger.info("Fetching AT ranking from %s", url)
    try:
        soup = _get(url)
    except Exception as exc:
        logger.error("Failed to fetch AT ranking page: %s", exc)
        return []

    entries = []
    try:
        lignes = soup.find("div", class_="TCTT_lignes")
        rows = lignes.find_all("div", class_=re.compile(r"^TCTT_ligne"))
        for row in rows[1:]:  # skip header row
            p_tags = row.find_all("p")
            if len(p_tags) < 7:
                continue
            ema_id = p_tags[2].get_text(strip=True)
            if not ema_id.isdigit():
                continue
            ema_rank_str = p_tags[0].get_text(strip=True)
            last_name = p_tags[3].get_text(strip=True).title()
            first_name = p_tags[4].get_text(strip=True).title()
            total_str = re.sub(r"[^\d]", "", p_tags[6].get_text(strip=True))
            try:
                total_points = int(total_str) if total_str else 0
                ema_rank = int(ema_rank_str) if ema_rank_str.isdigit() else 0
            except ValueError:
                continue
            entries.append(
                {
                    "ema_id": ema_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "ema_rank": ema_rank,
                    "total_points": total_points,
                }
            )
    except Exception as exc:
        logger.error("Error parsing AT ranking page: %s", exc)

    entries.sort(key=lambda x: x["total_points"], reverse=True)
    logger.info("Found %d AT ranking entries", len(entries))
    return entries


def scrape_player_results(ema_id: str, start_date, end_date) -> list[dict]:
    """
    Fetch riichi EMA tournament results for one player, filtered to the quota period.

    Returns a list of dicts:
      {tournament_name, country_code, end_date (date), position, player_count}
    """
    url = f"{URLBASE}Players/{ema_id}.html"
    try:
        soup = _get(url)
    except Exception as exc:
        logger.error("Failed to fetch player page for %s: %s", ema_id, exc)
        return []

    results = []
    try:
        # Find the Riichi results table: among all tables with HallFame_ cells,
        # pick the one whose nearest preceding <h3> contains "Riichi".
        # For players who only have Riichi results the first HallFame table is used.
        # This approach is robust against navigation headings also named "Riichi".
        hallFame_tables = [
            t for t in soup.find_all("table") if t.find("td", class_=lambda c: c and c.startswith("HallFame_"))
        ]

        results_table = None
        if len(hallFame_tables) == 1:
            results_table = hallFame_tables[0]
        elif len(hallFame_tables) > 1:
            for tbl in hallFame_tables:
                prev_h3 = tbl.find_previous("h3")
                if prev_h3 and "riichi" in prev_h3.get_text(strip=True).lower():
                    results_table = tbl
                    break

        if results_table is None:
            logger.warning("No Riichi results table found for player %s", ema_id)
            return results

        for row in results_table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 7:
                continue
            # Skip the header row (first cell contains "Id" text, not a digit)
            id_text = cells[0].get_text(strip=True)
            if not id_text.isdigit():
                continue
            try:
                # Cell 1: date range, e.g. "18-19 April 2026"
                date_text = cells[1].get_text(strip=True)
                t_end_date = _parse_end_date(date_text)
                if t_end_date is None:
                    logger.warning("Could not parse date %r for player %s", date_text, ema_id)
                    continue

                if not (start_date <= t_end_date <= end_date):
                    continue

                # Cell 2: country flag img + city
                flag_img = cells[2].find("img")
                country_code = "??"
                if flag_img:
                    m = COUNTRY_FLAG_PATTERN.search(flag_img.get("src", ""))
                    if m:
                        country_code = m.group(1)

                # Cell 3: tournament name and EMA URL
                cell3 = cells[3]
                tournament_name = cell3.get_text(strip=True)
                ema_tournament_url = ""
                link = cell3.find("a")
                if link and link.get("href"):
                    # href is like "../Tournament/TR_RCR_409.html" — make absolute
                    href = link["href"].lstrip("./")
                    ema_tournament_url = f"{URLBASE}{href}"

                # Cell 5: rank like "15/64" (may be inside a FONT tag)
                rank_text = cells[5].get_text(strip=True)
                if "/" not in rank_text:
                    logger.warning("Unexpected rank format %r for player %s", rank_text, ema_id)
                    continue
                pos_str, count_str = rank_text.split("/", 1)
                position = int(pos_str.strip())
                player_count = int(count_str.strip())

                results.append(
                    {
                        "tournament_name": tournament_name,
                        "ema_tournament_url": ema_tournament_url,
                        "country_code": country_code,
                        "end_date": t_end_date,
                        "position": position,
                        "player_count": player_count,
                    }
                )
            except Exception as exc:
                logger.warning("Could not parse result row for player %s: %s", ema_id, exc)
                continue
    except Exception as exc:
        logger.error("Error parsing player results for %s: %s", ema_id, exc)

    return results


def run_full_scrape(quota_period) -> tuple[int, int]:
    """
    Scrape all AT players and store their tournament results for the given quota period.

    Returns (created_count, skipped_count).
    """
    at_players = scrape_at_players()
    created = skipped = 0

    for player_info in at_players:
        ema_id = player_info["ema_id"]
        results = scrape_player_results(ema_id, quota_period.start_date, quota_period.end_date)

        for r in results:
            is_at = r["country_code"].lower() == "at"
            from austria_ranking.calculator import calculate_points

            points = calculate_points(r["player_count"], r["position"])

            _, created_flag = EmaTournamentResult.objects.get_or_create(
                quota_period=quota_period,
                ema_id=ema_id,
                tournament_name=r["tournament_name"],
                end_date=r["end_date"],
                defaults={
                    "first_name": player_info["first_name"],
                    "last_name": player_info["last_name"],
                    "tournament_country_code": r["country_code"],
                    "position": r["position"],
                    "player_count": r["player_count"],
                    "points": points,
                    "is_austrian_tournament": is_at,
                    "ema_tournament_url": r.get("ema_tournament_url", ""),
                },
            )
            if created_flag:
                created += 1
            else:
                skipped += 1

    return created, skipped
