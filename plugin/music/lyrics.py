import re
import requests
from bs4 import BeautifulSoup

from pyrogram import Client, filters
from pyrogram.types import Message


# -----------------------------
# Helper: Clean HTML text
# -----------------------------
def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\n\n", "\n")
    return text.strip()


# -----------------------------
# Scrape lyrics from search result links
# -----------------------------
def scrape_lyrics(query: str):
    search_url = f"https://www.google.com/search?q={query}+lyrics"
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0 Safari/537.36"
        )
    }

    html = requests.get(search_url, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")

    # Google "featured lyrics"
    featured = soup.find("div", class_="BNeawe tAd8D AP7Wnd")
    if featured:
        return clean(featured.get_text())

    # fallback: find first lyrics site link
    links = soup.find_all("a", href=True)
    possible_sites = ["genius.com", "azlyrics.com", "lyricfind", "lyrics", "musixmatch"]

    for link in links:
        url = link["href"]
        if any(site in url for site in possible_sites):
            url = url.replace("/url?q=", "").split("&")[0]
            try:
                page = requests.get(url, headers=headers).text
                page_soup = BeautifulSoup(page, "html.parser")

                # Genius
                if "genius.com" in url:
                    divs = page_soup.find_all("div", {"data-lyrics-container": "true"})
                    if divs:
                        text = "\n".join([clean(d.get_text()) for d in divs])
                        return text

                # AZLyrics
                if "azlyrics" in url:
                    div = page_soup.find("div", class_=None)
                    if div:
                        return clean(div.get_text())
            except:
                continue

    return None


# -----------------------------
# /lyrics command
# -----------------------------
@Client.on_message(filters.command(["lyrics", "ly"]) & ~filters.private)
async def lyrics_cmd(client: Client, message: Message):
    if len(message.command) == 1:
        return await message.reply_text(
            "> 🎶 **Usage:** `/lyrics <song name>`",
            quote=True
        )

    query = " ".join(message.command[1:])
    await message.reply_text("> 🔍 **Searching lyrics...**", quote=True)

    try:
        text = scrape_lyrics(query)

        if not text:
            return await message.reply_text(
                "> ❌ Could not find lyrics anywhere.",
                quote=True
            )

        # Split into chunks if long
        chunks = []
        while len(text) > 4000:
            chunks.append(text[:4000])
            text = text[4000:]
        chunks.append(text)

        # Send in multiple messages if needed
        for part in chunks:
            await message.reply_text(f"🎶 **Lyrics for:** `{query
