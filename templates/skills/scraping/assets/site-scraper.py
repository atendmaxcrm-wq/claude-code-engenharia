#!/usr/bin/env python3
"""
Generic Website Scraper using Playwright + Stealth

Crawls an entire website, extracting all text content and downloading images.
Navigates through all internal links recursively.

Usage:
    python3 site-scraper.py --url "https://example.com" --output "./output"
    python3 site-scraper.py --url "https://example.com" --output "./output" --max-pages 50 --delay 2

Output:
    - content.json: Structured text content per page
    - images/: Downloaded images organized by page slug
    Logs go to stderr, final summary JSON to stdout.
"""

import asyncio
import json
import sys
import os
import re
import argparse
import hashlib
import time
from urllib.parse import urljoin, urlparse, unquote


def log(msg):
    print(f"[site-scraper] {msg}", file=sys.stderr)


def slugify(text):
    """Convert a URL path to a safe filename slug."""
    text = unquote(text)
    text = re.sub(r'https?://', '', text)
    text = re.sub(r'[^\w\s-]', '_', text)
    text = re.sub(r'[-\s]+', '-', text).strip('-_')
    return text[:100] if text else 'home'


def is_same_domain(url, base_domain):
    """Check if URL belongs to the same domain."""
    try:
        parsed = urlparse(url)
        return parsed.netloc == base_domain or parsed.netloc == ''
    except Exception:
        return False


def is_valid_page_url(url):
    """Filter out non-page URLs (assets, anchors, etc)."""
    skip_extensions = (
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico',
        '.css', '.js', '.pdf', '.zip', '.mp4', '.mp3', '.wav',
        '.woff', '.woff2', '.ttf', '.eot',
    )
    parsed = urlparse(url)
    path = parsed.path.lower()

    if any(path.endswith(ext) for ext in skip_extensions):
        return False
    if parsed.fragment and not parsed.path:
        return False
    if parsed.scheme and parsed.scheme not in ('http', 'https'):
        return False

    return True


def normalize_url(url):
    """Normalize URL for deduplication."""
    parsed = urlparse(url)
    # Remove fragment and trailing slash
    path = parsed.path.rstrip('/')
    if not path:
        path = ''
    return f"{parsed.scheme}://{parsed.netloc}{path}"


async def download_image(page, img_url, output_dir, page_slug, img_index):
    """Download a single image using the browser context."""
    try:
        ext_match = re.search(r'\.(jpg|jpeg|png|gif|webp|svg|avif)', img_url.lower())
        ext = ext_match.group(0) if ext_match else '.jpg'
        filename = f"{page_slug}_{img_index:03d}{ext}"
        filepath = os.path.join(output_dir, filename)

        response = await page.request.get(img_url, timeout=15000)
        if response.ok:
            body = await response.body()
            if len(body) > 500:  # Skip tiny placeholders/tracking pixels
                with open(filepath, 'wb') as f:
                    f.write(body)
                return {"url": img_url, "file": filename, "size": len(body)}
    except Exception as e:
        log(f"  Failed to download image: {img_url[:80]} - {e}")
    return None


async def extract_page_content(page, url):
    """Extract all text content and image URLs from a page."""
    content = await page.evaluate("""
        () => {
            // Helper to get visible text
            function getVisibleText(el) {
                if (!el) return '';
                const style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden') return '';
                return el.innerText || el.textContent || '';
            }

            // Title
            const title = document.title || '';
            const h1 = document.querySelector('h1');
            const h1Text = h1 ? h1.innerText.trim() : '';

            // Meta tags
            const metaDesc = document.querySelector('meta[name="description"]');
            const metaKeys = document.querySelector('meta[name="keywords"]');
            const ogImage = document.querySelector('meta[property="og:image"]');
            const ogTitle = document.querySelector('meta[property="og:title"]');
            const ogDesc = document.querySelector('meta[property="og:description"]');

            // All headings
            const headings = [];
            document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
                const text = h.innerText.trim();
                if (text) headings.push({ level: h.tagName, text: text });
            });

            // All paragraphs and text blocks
            const paragraphs = [];
            document.querySelectorAll('p, li, blockquote, figcaption, .text, [class*="description"], [class*="content"]').forEach(el => {
                const text = el.innerText.trim();
                if (text && text.length > 10) {
                    paragraphs.push(text);
                }
            });

            // Deduplicate paragraphs (nested elements can produce duplicates)
            const uniqueParagraphs = [...new Set(paragraphs)];

            // All links (internal)
            const links = [];
            document.querySelectorAll('a[href]').forEach(a => {
                links.push({
                    href: a.href,
                    text: a.innerText.trim().substring(0, 100)
                });
            });

            // All images
            const images = [];
            const seenSrcs = new Set();

            // <img> tags
            document.querySelectorAll('img').forEach(img => {
                const src = img.src || img.dataset.src || img.dataset.lazySrc || '';
                if (src && !seenSrcs.has(src) && !src.startsWith('data:')) {
                    seenSrcs.add(src);
                    images.push({
                        src: src,
                        alt: img.alt || '',
                        width: img.naturalWidth || img.width || 0,
                        height: img.naturalHeight || img.height || 0
                    });
                }
            });

            // <source> inside <picture>
            document.querySelectorAll('picture source').forEach(source => {
                const srcset = source.srcset || '';
                const firstSrc = srcset.split(',')[0].trim().split(' ')[0];
                if (firstSrc && !seenSrcs.has(firstSrc) && !firstSrc.startsWith('data:')) {
                    seenSrcs.add(firstSrc);
                    images.push({ src: firstSrc, alt: '', width: 0, height: 0 });
                }
            });

            // Background images from inline styles
            document.querySelectorAll('[style*="background"]').forEach(el => {
                const style = el.getAttribute('style') || '';
                const match = style.match(/url\\(['"]*([^'"\\)]+)['"]*\\)/);
                if (match && match[1] && !seenSrcs.has(match[1]) && !match[1].startsWith('data:')) {
                    seenSrcs.add(match[1]);
                    images.push({ src: match[1], alt: 'background', width: 0, height: 0 });
                }
            });

            // og:image
            if (ogImage && ogImage.content && !seenSrcs.has(ogImage.content)) {
                seenSrcs.add(ogImage.content);
                images.push({ src: ogImage.content, alt: 'og:image', width: 0, height: 0 });
            }

            return {
                title: title,
                h1: h1Text,
                meta: {
                    description: metaDesc ? metaDesc.content : '',
                    keywords: metaKeys ? metaKeys.content : '',
                    og_image: ogImage ? ogImage.content : '',
                    og_title: ogTitle ? ogTitle.content : '',
                    og_description: ogDesc ? ogDesc.content : ''
                },
                headings: headings,
                paragraphs: uniqueParagraphs,
                links: links,
                images: images
            };
        }
    """)

    return content


async def scrape_site(base_url, output_dir, max_pages=100, delay=2):
    """Crawl entire site and extract content + images."""
    from playwright.async_api import async_playwright
    from playwright_stealth import Stealth

    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc

    # Create output directories
    images_dir = os.path.join(output_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    visited = set()
    to_visit = [normalize_url(base_url)]
    all_pages = []
    total_images_downloaded = 0

    log(f"Starting crawl of {base_url}")
    log(f"Output directory: {output_dir}")
    log(f"Max pages: {max_pages}, Delay: {delay}s")

    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
        )

        page = await context.new_page()

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)

            if url in visited:
                continue

            visited.add(url)
            page_num = len(visited)

            log(f"[{page_num}/{max_pages}] Crawling: {url}")

            try:
                response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)

                if not response or response.status >= 400:
                    log(f"  Skipping (status {response.status if response else 'no response'})")
                    continue

                # Wait for dynamic content to load
                await page.wait_for_timeout(3000)

                # Scroll to trigger lazy loading
                for i in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1000)

                # Scroll back to top
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(500)

                # Extract content
                content = await extract_page_content(page, url)

                page_slug = slugify(urlparse(url).path or 'home')

                # Discover new internal links
                for link in content.get('links', []):
                    href = link.get('href', '')
                    if not href:
                        continue

                    # Resolve relative URLs
                    full_url = urljoin(url, href)
                    normalized = normalize_url(full_url)

                    if (is_same_domain(full_url, base_domain)
                            and normalized not in visited
                            and normalized not in to_visit
                            and is_valid_page_url(full_url)):
                        to_visit.append(normalized)

                # Download images
                downloaded_images = []
                for idx, img in enumerate(content.get('images', [])):
                    src = img.get('src', '')
                    if not src:
                        continue

                    # Resolve relative image URLs
                    full_src = urljoin(url, src)
                    result = await download_image(page, full_src, images_dir, page_slug, idx)
                    if result:
                        downloaded_images.append(result)
                        total_images_downloaded += 1

                # Build page data
                page_data = {
                    "url": url,
                    "slug": page_slug,
                    "title": content.get('title', ''),
                    "h1": content.get('h1', ''),
                    "meta": content.get('meta', {}),
                    "headings": content.get('headings', []),
                    "paragraphs": content.get('paragraphs', []),
                    "images": downloaded_images,
                    "internal_links_found": len([
                        l for l in content.get('links', [])
                        if is_same_domain(l.get('href', ''), base_domain)
                    ]),
                }

                all_pages.append(page_data)

                log(f"  Title: {content.get('title', 'N/A')[:60]}")
                log(f"  Paragraphs: {len(content.get('paragraphs', []))}, Images: {len(downloaded_images)}, Links found: {page_data['internal_links_found']}")

            except Exception as e:
                log(f"  Error crawling {url}: {e}")

            # Rate limiting
            if to_visit:
                await asyncio.sleep(delay)

        await browser.close()

    # Save content.json
    content_path = os.path.join(output_dir, 'content.json')
    with open(content_path, 'w', encoding='utf-8') as f:
        json.dump(all_pages, f, ensure_ascii=False, indent=2)

    log(f"\n{'='*50}")
    log(f"Crawl complete!")
    log(f"Pages scraped: {len(all_pages)}")
    log(f"Images downloaded: {total_images_downloaded}")
    log(f"Content saved to: {content_path}")
    log(f"Images saved to: {images_dir}")
    log(f"Remaining in queue: {len(to_visit)} (limit was {max_pages})")
    log(f"{'='*50}")

    # Output summary to stdout
    summary = {
        "status": "success",
        "base_url": base_url,
        "pages_scraped": len(all_pages),
        "images_downloaded": total_images_downloaded,
        "output_dir": output_dir,
        "content_file": content_path,
        "images_dir": images_dir,
        "pages": [{"url": p["url"], "title": p["title"], "paragraphs": len(p["paragraphs"]), "images": len(p["images"])} for p in all_pages]
    }

    return summary


async def main():
    parser = argparse.ArgumentParser(description="Generic website scraper")
    parser.add_argument("--url", required=True, help="Base URL to crawl")
    parser.add_argument("--output", required=True, help="Output directory path")
    parser.add_argument("--max-pages", type=int, default=100, help="Maximum pages to crawl (default: 100)")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests in seconds (default: 2)")
    args = parser.parse_args()

    summary = await scrape_site(args.url, args.output, args.max_pages, args.delay)
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
