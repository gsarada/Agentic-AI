import json
import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from backend.schemas.product import RawProductData
from backend.utils.logging import get_logger, log_duration

logger = get_logger(__name__)

JS_HEAVY_DOMAINS = {
    "nike.com",
    "zara.com",
    "asos.com",
    "uniqlo.com",
    "shein.com",
    "hm.com",
    "myntra.com",
}


class ProductScraperService:
  async def fetch_html(self, url: str) -> str:
      domain = urlparse(url).netloc.replace("www.", "")
      use_playwright = any(domain.endswith(d) for d in JS_HEAVY_DOMAINS)

      if use_playwright:
          return await self._fetch_with_playwright(url)
      return await self._fetch_with_httpx(url)

  async def _fetch_with_httpx(self, url: str) -> str:
      headers = {
          "User-Agent": (
              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
          )
      }
      async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
          response = await client.get(url, headers=headers)
          response.raise_for_status()
          return response.text

  async def _fetch_with_playwright(self, url: str) -> str:
      try:
          from playwright.async_api import async_playwright
      except ImportError as exc:
          logger.warning("playwright_not_installed", error=str(exc))
          return await self._fetch_with_httpx(url)

      try:
          async with async_playwright() as p:
              browser = await p.chromium.launch(headless=True)
              page = await browser.new_page()
              await page.goto(url, wait_until="networkidle", timeout=60000)
              html = await page.content()
              await browser.close()
              return html
      except Exception as exc:
          logger.error("playwright_fetch_failed", error=str(exc), url=url)
          return await self._fetch_with_httpx(url)

  async def scrape(self, url: str) -> RawProductData:
      with log_duration(logger, "product_scrape", url=url):
          html = await self.fetch_html(url)
          return self.parse_html(url, html)

  def parse_html(self, url: str, html: str) -> RawProductData:
      soup = BeautifulSoup(html, "lxml")

      name = self._first_text(
          soup,
          [
              ("meta", {"property": "og:title"}),
              ("h1", {}),
              ("title", {}),
          ],
          attr="content",
      )
      brand = self._first_text(soup, [("meta", {"property": "product:brand"}), ("span", {"class": re.compile("brand", re.I)})], attr="content")
      price = self._first_text(
          soup,
          [
              ("meta", {"property": "product:price:amount"}),
              ("span", {"class": re.compile("price", re.I)}),
          ],
          attr="content",
      )
      description = self._first_text(
          soup,
          [
              ("meta", {"property": "og:description"}),
              ("meta", {"name": "description"}),
              ("div", {"class": re.compile("description", re.I)}),
          ],
          attr="content",
      )
      material = self._first_text(soup, [("div", {"class": re.compile("material|fabric", re.I)})])
      fit = self._first_text(soup, [("div", {"class": re.compile("fit", re.I)})])

      images = self._extract_images(soup, url)
      sizes = self._extract_sizes(soup)
      reviews = self._extract_reviews(soup)
      size_chart = self._extract_size_chart(soup)
      ratings = self._first_text(soup, [("span", {"class": re.compile("rating|stars", re.I)})])

      return RawProductData(
          name=name or "Unknown Product",
          brand=brand or "",
          price=price or "",
          available_sizes=sizes,
          product_images=images,
          description=description or "",
          material=material or "",
          fit=fit or "",
          size_chart=size_chart,
          reviews=reviews,
          ratings=ratings or "",
          source_url=url,
      )

  def _first_text(self, soup: BeautifulSoup, selectors: list, attr: str | None = None) -> str:
      for tag, attrs in selectors:
          element = soup.find(tag, attrs)
          if not element:
              continue
          if attr and element.has_attr(attr):
              return str(element[attr]).strip()
          text = element.get_text(" ", strip=True)
          if text:
              return text
      return ""

  def _extract_images(self, soup: BeautifulSoup, base_url: str) -> list[str]:
      images: list[str] = []
      for meta in soup.find_all("meta", property="og:image"):
          if meta.get("content"):
              images.append(urljoin(base_url, meta["content"]))
      for img in soup.find_all("img"):
          src = img.get("src") or img.get("data-src")
          if src and any(token in src.lower() for token in ("product", "pdp", "item")):
              images.append(urljoin(base_url, src))
      return list(dict.fromkeys(images))[:10]

  def _extract_sizes(self, soup: BeautifulSoup) -> list[str]:
      sizes: list[str] = []
      for element in soup.find_all(["button", "option", "span", "li"]):
          text = element.get_text(strip=True)
          if re.fullmatch(r"(XXS|XS|S|M|L|XL|XXL|XXXL|\d{1,2}|\d{1,2}\.\d)", text, re.I):
              sizes.append(text.upper())
      return list(dict.fromkeys(sizes))

  def _extract_reviews(self, soup: BeautifulSoup) -> list[str]:
      reviews: list[str] = []
      for element in soup.find_all(["div", "p", "span"], class_=re.compile("review", re.I)):
          text = element.get_text(" ", strip=True)
          if len(text) > 40:
              reviews.append(text[:500])
      return reviews[:20]

  def _extract_size_chart(self, soup: BeautifulSoup) -> dict:
      table = soup.find("table", class_=re.compile("size", re.I)) or soup.find("table")
      if not table:
          return {}
      rows = []
      for tr in table.find_all("tr"):
          cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
          if cells:
              rows.append(cells)
      if not rows:
          return {}
      headers = rows[0]
      chart = {}
      for row in rows[1:]:
          if len(row) == len(headers):
              chart[row[0]] = dict(zip(headers[1:], row[1:]))
      return chart
