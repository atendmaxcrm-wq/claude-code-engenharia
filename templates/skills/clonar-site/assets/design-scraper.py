#!/usr/bin/env python3
"""
Design System & Animation Scraper using Playwright + Stealth

Extracts design tokens (colors, typography, spacing, shadows), CSS animations,
transitions, JS animation library usage, layout structure, and captures
screenshots + scroll video from any website.

Usage:
    python3 design-scraper.py --url "https://example.com" --output "./output/design"
    python3 design-scraper.py --url "https://example.com" --output "./output/design" --video --responsive

Output:
    - design-data.json: Complete design system data
    - screenshots/: Full-page + per-section screenshots
    - video/: Scroll recording (if --video flag)
    Logs go to stderr, final summary JSON to stdout.
"""

import asyncio
import json
import sys
import os
import re
import argparse
from urllib.parse import urlparse


def log(msg):
    print(f"[design-scraper] {msg}", file=sys.stderr)


def rgb_to_hex(rgb_str):
    """Convert rgb(r, g, b) or rgba(r, g, b, a) to hex."""
    match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', rgb_str)
    if match:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return f"#{r:02x}{g:02x}{b:02x}"
    return rgb_str


EXTRACT_DESIGN_TOKENS_JS = """
() => {
    const result = {
        cssVariables: {},
        colors: {},
        typography: {},
        spacing: {},
        shadows: [],
        borderRadius: [],
        gradients: [],
        opacities: []
    };

    // 1. CSS Custom Properties from :root
    const rootStyles = getComputedStyle(document.documentElement);
    const sheets = document.styleSheets;
    for (let i = 0; i < sheets.length; i++) {
        try {
            const rules = sheets[i].cssRules || sheets[i].rules;
            for (let j = 0; j < rules.length; j++) {
                if (rules[j].selectorText === ':root' || rules[j].selectorText === ':root, :host') {
                    const style = rules[j].style;
                    for (let k = 0; k < style.length; k++) {
                        const prop = style[k];
                        if (prop.startsWith('--')) {
                            result.cssVariables[prop] = style.getPropertyValue(prop).trim();
                        }
                    }
                }
            }
        } catch (e) { /* CORS */ }
    }

    // 2. Collect colors, typography, spacing from all visible elements
    const colorMap = {};
    const fontMap = {};
    const spacingMap = {};
    const shadowSet = new Set();
    const radiusSet = new Set();
    const gradientSet = new Set();
    const opacitySet = new Set();

    const elements = document.querySelectorAll('body *');
    const maxElements = Math.min(elements.length, 2000);

    for (let i = 0; i < maxElements; i++) {
        const el = elements[i];
        const tag = el.tagName.toLowerCase();

        // Skip invisible and script/style elements
        if (['script', 'style', 'noscript', 'link', 'meta', 'br', 'hr'].includes(tag)) continue;
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) continue;

        const cs = getComputedStyle(el);

        // Colors
        const colorProps = ['color', 'backgroundColor', 'borderTopColor', 'borderBottomColor', 'borderLeftColor', 'borderRightColor'];
        colorProps.forEach(prop => {
            const val = cs[prop];
            if (val && val !== 'rgba(0, 0, 0, 0)' && val !== 'transparent') {
                colorMap[val] = (colorMap[val] || 0) + 1;
            }
        });

        // Typography (only for text-bearing elements)
        const textTags = ['h1','h2','h3','h4','h5','h6','p','a','span','li','blockquote','figcaption','button','label','input','textarea','td','th','div'];
        if (textTags.includes(tag) && el.innerText && el.innerText.trim().length > 0) {
            const fontKey = `${cs.fontFamily}|${cs.fontSize}|${cs.fontWeight}|${cs.lineHeight}|${cs.letterSpacing}`;
            if (!fontMap[fontKey]) {
                fontMap[fontKey] = {
                    fontFamily: cs.fontFamily,
                    fontSize: cs.fontSize,
                    fontWeight: cs.fontWeight,
                    lineHeight: cs.lineHeight,
                    letterSpacing: cs.letterSpacing,
                    count: 0,
                    sampleTag: tag,
                    sampleText: el.innerText.trim().substring(0, 60)
                };
            }
            fontMap[fontKey].count++;
        }

        // Spacing
        ['paddingTop','paddingRight','paddingBottom','paddingLeft','marginTop','marginRight','marginBottom','marginLeft','gap'].forEach(prop => {
            const val = cs[prop];
            if (val && val !== '0px' && val !== 'normal' && val !== 'auto') {
                spacingMap[val] = (spacingMap[val] || 0) + 1;
            }
        });

        // Shadows
        if (cs.boxShadow && cs.boxShadow !== 'none') shadowSet.add(cs.boxShadow);
        if (cs.textShadow && cs.textShadow !== 'none') shadowSet.add('text: ' + cs.textShadow);

        // Border radius
        if (cs.borderRadius && cs.borderRadius !== '0px') radiusSet.add(cs.borderRadius);

        // Gradients
        const bg = cs.backgroundImage;
        if (bg && bg !== 'none' && (bg.includes('gradient') || bg.includes('linear') || bg.includes('radial'))) {
            gradientSet.add(bg);
        }

        // Opacity
        if (cs.opacity && cs.opacity !== '1') opacitySet.add(cs.opacity);
    }

    // Sort colors by frequency
    result.colors = Object.entries(colorMap)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 50)
        .map(([color, count]) => ({ raw: color, count }));

    // Sort typography by count
    result.typography = Object.values(fontMap)
        .sort((a, b) => b.count - a.count)
        .slice(0, 30);

    // Sort spacing by frequency
    result.spacing = Object.entries(spacingMap)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 30)
        .map(([value, count]) => ({ value, count }));

    result.shadows = Array.from(shadowSet);
    result.borderRadius = Array.from(radiusSet);
    result.gradients = Array.from(gradientSet);
    result.opacities = Array.from(opacitySet);

    return result;
}
"""

EXTRACT_ANIMATIONS_JS = """
() => {
    const result = {
        keyframes: [],
        cssAnimations: [],
        cssTransitions: [],
        hoverRules: [],
        jsLibraries: {},
        scrollTriggerElements: [],
        dataAttributes: [],
        webAnimations: [],
        videos: [],
        framerConfig: {}
    };

    // 1. Extract @keyframes from stylesheets
    const seenKeyframes = new Set();
    const sheets = document.styleSheets;
    for (let i = 0; i < sheets.length; i++) {
        try {
            const rules = sheets[i].cssRules || sheets[i].rules;
            for (let j = 0; j < rules.length; j++) {
                const rule = rules[j];
                if (rule.type === 7 && !seenKeyframes.has(rule.name)) {
                    seenKeyframes.add(rule.name);
                    const frames = [];
                    for (let k = 0; k < rule.cssRules.length; k++) {
                        frames.push({ offset: rule.cssRules[k].keyText, style: rule.cssRules[k].style.cssText });
                    }
                    result.keyframes.push({ name: rule.name, frames });
                }
                if (rule.type === 1 && rule.selectorText && rule.selectorText.includes(':hover')) {
                    result.hoverRules.push({ selector: rule.selectorText, style: rule.style.cssText });
                }
            }
        } catch (e) { /* CORS */ }
    }

    // 2. CSS animations and transitions from elements
    const seenAnimations = new Set();
    const seenTransitions = new Set();
    const elements = document.querySelectorAll('body *');
    const maxElements = Math.min(elements.length, 2000);

    for (let i = 0; i < maxElements; i++) {
        const el = elements[i];
        const cs = getComputedStyle(el);

        if (cs.animationName && cs.animationName !== 'none') {
            const key = `${cs.animationName}|${el.tagName}|${el.className}`;
            if (!seenAnimations.has(key)) {
                seenAnimations.add(key);
                result.cssAnimations.push({
                    element: el.tagName.toLowerCase(),
                    classes: el.className ? el.className.toString().substring(0, 100) : '',
                    animationName: cs.animationName,
                    duration: cs.animationDuration,
                    timingFunction: cs.animationTimingFunction,
                    delay: cs.animationDelay,
                    iterationCount: cs.animationIterationCount,
                    direction: cs.animationDirection,
                    fillMode: cs.animationFillMode
                });
            }
        }

        if (cs.transitionProperty && cs.transitionProperty !== 'all' && cs.transitionDuration !== '0s') {
            const key = `${cs.transitionProperty}|${cs.transitionDuration}|${el.tagName}`;
            if (!seenTransitions.has(key)) {
                seenTransitions.add(key);
                result.cssTransitions.push({
                    element: el.tagName.toLowerCase(),
                    classes: el.className ? el.className.toString().substring(0, 100) : '',
                    property: cs.transitionProperty,
                    duration: cs.transitionDuration,
                    timingFunction: cs.transitionTimingFunction,
                    delay: cs.transitionDelay
                });
            }
        }
    }

    // 3. Web Animations API — captures runtime Framer Motion / GSAP keyframes
    try {
        const allAnimated = document.getAnimations();
        allAnimated.forEach(anim => {
            try {
                const target = anim.effect && anim.effect.target;
                if (!target) return;
                const timing = anim.effect.getTiming ? anim.effect.getTiming() : {};
                const kfs = anim.effect.getKeyframes ? anim.effect.getKeyframes() : [];
                if (kfs.length === 0) return;

                const heading = target.querySelector && target.querySelector('h1,h2,h3,h4,p,span');
                result.webAnimations.push({
                    element: target.tagName ? target.tagName.toLowerCase() : 'unknown',
                    classes: target.className ? target.className.toString().substring(0, 100) : '',
                    id: target.id || '',
                    text: (target.innerText || '').substring(0, 60),
                    childText: heading ? heading.innerText.substring(0, 60) : '',
                    duration: timing.duration || null,
                    delay: timing.delay || 0,
                    easing: timing.easing || 'linear',
                    iterations: timing.iterations || 1,
                    fill: timing.fill || 'auto',
                    direction: timing.direction || 'normal',
                    playState: anim.playState || 'unknown',
                    keyframes: kfs.map(kf => {
                        const obj = {};
                        for (const k of Object.keys(kf)) {
                            if (k !== 'composite' && k !== 'computedOffset') obj[k] = kf[k];
                        }
                        return obj;
                    })
                });
            } catch (e) {}
        });
    } catch (e) {}

    // 4. Detect JS animation libraries
    result.jsLibraries = {
        gsap: !!(window.gsap || window.TweenMax || window.TimelineMax || window.TweenLite),
        gsapVersion: window.gsap ? window.gsap.version : null,
        framerMotion: !!(window.__FRAMER_MOTION_VERSION__),
        framerMotionVersion: window.__FRAMER_MOTION_VERSION__ || null,
        framerSite: !!document.querySelector('[data-framer-component-type]'),
        aos: !!window.AOS,
        lenis: !!(window.Lenis || window.__lenis),
        locomotiveScroll: !!window.LocomotiveScroll,
        scrollTrigger: !!(window.ScrollTrigger || (window.gsap && window.gsap.plugins && window.gsap.plugins.scrollTrigger)),
        animejs: !!window.anime,
        threejs: !!window.THREE,
        popmotion: !!window.popmotion,
        barbajs: !!window.barba
    };

    // 5. Elements with scroll-trigger data attributes
    const scrollAttrs = ['data-aos', 'data-scroll', 'data-scroll-speed', 'data-framer-appear-id',
                          'data-framer-appear-animation', 'data-animate', 'data-animation',
                          'data-scroll-section', 'data-speed', 'data-lag', 'data-parallax'];
    scrollAttrs.forEach(attr => {
        document.querySelectorAll(`[${attr}]`).forEach(el => {
            const heading = el.querySelector('h1,h2,h3,h4,h5,p,span');
            result.scrollTriggerElements.push({
                attribute: attr,
                value: el.getAttribute(attr),
                element: el.tagName.toLowerCase(),
                classes: el.className ? el.className.toString().substring(0, 80) : '',
                id: el.id || '',
                text: (el.innerText || '').substring(0, 60),
                childHeading: heading ? heading.innerText.substring(0, 60) : '',
                rect: {
                    top: Math.round(el.getBoundingClientRect().top + window.scrollY),
                    height: Math.round(el.getBoundingClientRect().height)
                },
                initialStyles: {
                    opacity: getComputedStyle(el).opacity,
                    transform: getComputedStyle(el).transform
                }
            });
        });
    });

    // 6. Detect data-* attributes related to animation
    const allDataAttrs = new Set();
    document.querySelectorAll('body *').forEach(el => {
        Array.from(el.attributes).forEach(attr => {
            if (attr.name.startsWith('data-') &&
                (attr.name.includes('anim') || attr.name.includes('scroll') ||
                 attr.name.includes('motion') || attr.name.includes('transition') ||
                 attr.name.includes('delay') || attr.name.includes('duration') ||
                 attr.name.includes('appear') || attr.name.includes('parallax') ||
                 attr.name.includes('framer'))) {
                allDataAttrs.add(attr.name);
            }
        });
    });
    result.dataAttributes = Array.from(allDataAttrs);

    // 7. Extract embedded videos
    document.querySelectorAll('video').forEach(video => {
        const sources = Array.from(video.querySelectorAll('source')).map(s => ({
            src: s.src, type: s.type
        }));
        result.videos.push({
            type: 'video-tag',
            src: video.src || (sources[0] && sources[0].src) || '',
            sources: sources,
            poster: video.poster || '',
            autoplay: video.autoplay,
            loop: video.loop,
            muted: video.muted,
            width: video.videoWidth || video.width,
            height: video.videoHeight || video.height,
            parentClasses: video.parentElement ? video.parentElement.className.toString().substring(0, 80) : ''
        });
    });

    // 8. Framer-specific config extraction
    try {
        const framerScripts = Array.from(document.querySelectorAll('script'))
            .map(s => s.textContent || '')
            .filter(t => t.includes('framer') || t.includes('animation') || t.includes('variants'));
        const framerJsons = [];
        document.querySelectorAll('script[type="application/json"]').forEach(s => {
            try { framerJsons.push(JSON.parse(s.textContent)); } catch {}
        });
        result.framerConfig = {
            framerScriptsCount: framerScripts.length,
            framerJsonConfigs: framerJsons.slice(0, 3),
            framerComponentTypes: [...new Set(
                Array.from(document.querySelectorAll('[data-framer-component-type]'))
                    .map(el => el.getAttribute('data-framer-component-type'))
            )]
        };
    } catch (e) {}

    return result;
}
"""

EXTRACT_LAYOUT_JS = """
() => {
    const result = {
        sections: [],
        mediaQueries: [],
        breakpoints: [],
        containers: []
    };

    // 1. Detect sections
    const sectionSelectors = 'section, header, footer, main, nav, [role="banner"], [role="main"], [role="contentinfo"], [role="navigation"], [role="region"]';
    let sectionElements = document.querySelectorAll(sectionSelectors);

    // Fallback: if no semantic sections, use direct children of body
    if (sectionElements.length < 2) {
        sectionElements = document.querySelectorAll('body > *');
    }

    let sectionIndex = 0;
    sectionElements.forEach(el => {
        const tag = el.tagName.toLowerCase();
        if (['script', 'style', 'noscript', 'link'].includes(tag)) return;

        const rect = el.getBoundingClientRect();
        if (rect.height < 20) return; // Skip tiny elements

        const cs = getComputedStyle(el);
        sectionIndex++;

        // Try to detect a label for the section
        const heading = el.querySelector('h1, h2, h3');
        const headingText = heading ? heading.innerText.trim().substring(0, 60) : '';
        const id = el.id || '';
        const ariaLabel = el.getAttribute('aria-label') || '';

        result.sections.push({
            index: sectionIndex,
            tag: tag,
            id: id,
            classes: el.className ? el.className.toString().substring(0, 120) : '',
            label: headingText || ariaLabel || id || `${tag}-${sectionIndex}`,
            display: cs.display,
            flexDirection: cs.flexDirection !== 'row' ? cs.flexDirection : undefined,
            gridTemplateColumns: cs.gridTemplateColumns !== 'none' ? cs.gridTemplateColumns : undefined,
            justifyContent: cs.justifyContent,
            alignItems: cs.alignItems,
            gap: cs.gap !== 'normal' ? cs.gap : undefined,
            padding: cs.padding,
            maxWidth: cs.maxWidth !== 'none' ? cs.maxWidth : undefined,
            backgroundColor: cs.backgroundColor !== 'rgba(0, 0, 0, 0)' ? cs.backgroundColor : undefined,
            width: Math.round(rect.width),
            height: Math.round(rect.height),
            top: Math.round(rect.top + window.scrollY)
        });
    });

    // 2. Media queries
    const sheets = document.styleSheets;
    const mediaSet = new Set();
    for (let i = 0; i < sheets.length; i++) {
        try {
            const rules = sheets[i].cssRules || sheets[i].rules;
            for (let j = 0; j < rules.length; j++) {
                if (rules[j].type === 4) { // CSSMediaRule
                    const media = rules[j].media.mediaText;
                    if (!mediaSet.has(media)) {
                        mediaSet.add(media);
                        result.mediaQueries.push({
                            query: media,
                            ruleCount: rules[j].cssRules.length
                        });
                    }
                }
            }
        } catch (e) { /* CORS */ }
    }

    // 3. Detect breakpoints from media queries
    const bpSet = new Set();
    result.mediaQueries.forEach(mq => {
        const matches = mq.query.match(/(\\d+)px/g);
        if (matches) {
            matches.forEach(m => bpSet.add(parseInt(m)));
        }
    });
    result.breakpoints = Array.from(bpSet).sort((a, b) => a - b);

    // 4. Container patterns (elements with max-width)
    const containerSet = new Set();
    document.querySelectorAll('body *').forEach(el => {
        const cs = getComputedStyle(el);
        const mw = cs.maxWidth;
        if (mw && mw !== 'none' && mw !== '0px' && !mw.includes('%')) {
            const px = parseInt(mw);
            if (px > 300 && px < 3000) {
                containerSet.add(mw);
            }
        }
    });
    result.containers = Array.from(containerSet).sort((a, b) => parseInt(a) - parseInt(b));

    return result;
}
"""


CAPTURE_ELEMENT_STATES_JS = """
() => {
    // Capture current computed state of all elements that might animate on scroll
    // Strategy: find all elements that will likely animate on scroll
    // 1. Elements with animation data attributes
    const attrSelectors = '[data-framer-appear-id], [data-aos], [data-scroll], [data-animate], [data-animation]';
    const attrTargets = new Set(document.querySelectorAll(attrSelectors));

    // 2. Elements currently hidden (opacity:0) — these will fade in
    const allEls = document.querySelectorAll('body *');
    const hiddenEls = [];
    allEls.forEach(el => {
        const cs = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        if (cs.opacity === '0' && rect.height > 15 && !['script','style','noscript','link','meta'].includes(el.tagName.toLowerCase())) {
            hiddenEls.push(el);
        }
    });

    // 3. Framer component-type elements below the fold (likely will animate when scrolled to)
    const framerEls = document.querySelectorAll('[data-framer-component-type]');
    const viewportH = window.innerHeight;
    const belowFoldFramer = [];
    framerEls.forEach(el => {
        const rect = el.getBoundingClientRect();
        // Only include if below viewport and has content
        if (rect.top > viewportH * 0.8 && rect.height > 30) {
            belowFoldFramer.push(el);
        }
    });

    // Merge all (dedup via Set)
    const targetSet = new Set([...attrTargets, ...hiddenEls, ...belowFoldFramer]);
    const targets = Array.from(targetSet).slice(0, 300);
    const states = [];

    targets.forEach((el, i) => {
        const cs = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        const heading = el.querySelector('h1,h2,h3,h4,h5,p,span');

        // Also check inline style attribute for Framer-set values
        const inlineStyle = el.getAttribute('style') || '';

        states.push({
            index: i,
            element: el.tagName.toLowerCase(),
            classes: el.className ? el.className.toString().substring(0, 100) : '',
            id: el.id || '',
            text: (el.innerText || '').substring(0, 60),
            childHeading: heading ? heading.innerText.substring(0, 60) : '',
            appearId: el.getAttribute('data-framer-appear-id') || '',
            framerType: el.getAttribute('data-framer-component-type') || '',
            aosType: el.getAttribute('data-aos') || '',
            absoluteTop: Math.round(rect.top + window.scrollY),
            height: Math.round(rect.height),
            state: {
                opacity: cs.opacity,
                transform: cs.transform,
                visibility: cs.visibility,
                clipPath: cs.clipPath !== 'none' ? cs.clipPath : '',
                filter: cs.filter !== 'none' ? cs.filter : '',
                willChange: cs.willChange !== 'auto' ? cs.willChange : '',
                translate: cs.translate || '',
                scale: cs.scale || '',
                rotate: cs.rotate || '',
                inlineOpacity: inlineStyle.match(/opacity\s*:\s*([^;]+)/) ? inlineStyle.match(/opacity\s*:\s*([^;]+)/)[1].trim() : '',
                inlineTransform: inlineStyle.match(/transform\s*:\s*([^;]+)/) ? inlineStyle.match(/transform\s*:\s*([^;]+)/)[1].trim() : ''
            }
        });
    });

    return states;
}
"""

CAPTURE_RUNTIME_ANIMATIONS_JS = """
() => {
    // Capture ALL active Web Animations API animations at this moment
    const anims = document.getAnimations();
    const result = [];

    anims.forEach(anim => {
        try {
            const target = anim.effect && anim.effect.target;
            if (!target) return;

            const timing = anim.effect.getTiming ? anim.effect.getTiming() : {};
            const kfs = anim.effect.getKeyframes ? anim.effect.getKeyframes() : [];
            if (kfs.length === 0) return;

            const heading = target.querySelector && target.querySelector('h1,h2,h3,h4,h5,p,span');
            const rect = target.getBoundingClientRect();

            result.push({
                element: target.tagName ? target.tagName.toLowerCase() : 'unknown',
                classes: target.className ? target.className.toString().substring(0, 100) : '',
                id: target.id || '',
                text: (target.innerText || '').substring(0, 60),
                childText: heading ? heading.innerText.substring(0, 60) : '',
                absoluteTop: Math.round(rect.top + window.scrollY),
                appearId: target.getAttribute('data-framer-appear-id') || '',
                duration: timing.duration || null,
                delay: timing.delay || 0,
                easing: timing.easing || 'linear',
                iterations: timing.iterations || 1,
                fill: timing.fill || 'auto',
                direction: timing.direction || 'normal',
                playState: anim.playState || 'unknown',
                currentTime: anim.currentTime || 0,
                keyframes: kfs.map(kf => {
                    const obj = {};
                    for (const k of Object.keys(kf)) {
                        if (k !== 'composite' && k !== 'computedOffset') obj[k] = kf[k];
                    }
                    return obj;
                })
            });
        } catch (e) {}
    });

    return result;
}
"""

CAPTURE_HOVER_DIFFS_JS = """
(selector) => {
    const results = [];
    const elements = document.querySelectorAll(selector);
    const max = Math.min(elements.length, 20);

    for (let i = 0; i < max; i++) {
        const el = elements[i];
        const cs = getComputedStyle(el);

        results.push({
            element: el.tagName.toLowerCase(),
            classes: el.className ? el.className.toString().substring(0, 80) : '',
            text: (el.innerText || '').substring(0, 40),
            normalState: {
                transform: cs.transform,
                backgroundColor: cs.backgroundColor,
                color: cs.color,
                boxShadow: cs.boxShadow,
                borderColor: cs.borderTopColor,
                opacity: cs.opacity,
                scale: cs.scale,
                filter: cs.filter
            }
        });
    }
    return results;
}
"""


EXTRACT_SCROLL_BEHAVIOR_JS = """
() => {
    const result = {
        hijacked: false,
        snap: null,
        smoothScroll: null,
        pinnedSections: [],
        parallaxElements: [],
        cssScrollTimeline: [],
        scrollBehaviorCss: null,
        fullpageJs: false,
        bodyOverflow: null,
        htmlOverflow: null,
    };

    const htmlCs = getComputedStyle(document.documentElement);
    const bodyCs = getComputedStyle(document.body);

    // 1. Scroll hijacking detection
    result.bodyOverflow = bodyCs.overflow + ' / ' + bodyCs.overflowY;
    result.htmlOverflow = htmlCs.overflow + ' / ' + htmlCs.overflowY;

    const bodyHidden = bodyCs.overflow === 'hidden' || bodyCs.overflowY === 'hidden';
    const htmlHidden = htmlCs.overflow === 'hidden' || htmlCs.overflowY === 'hidden';

    if (bodyHidden || htmlHidden) {
        // Look for the scroll wrapper (fixed/absolute positioned child that moves)
        const candidates = document.querySelectorAll('body > div, body > main, body > section');
        let wrapper = null;
        candidates.forEach(el => {
            const cs = getComputedStyle(el);
            if (cs.position === 'fixed' || cs.position === 'absolute') {
                if (cs.transform !== 'none' || cs.willChange === 'transform' || cs.top !== 'auto') {
                    wrapper = el;
                }
            }
        });

        // Check for fullPage.js
        const fpSections = document.querySelectorAll('.fp-section, .section.fp-section, [data-anchor]');
        const isFullpage = !!(window.fullpage_api || fpSections.length > 0);

        // Check for Swiper vertical
        const swiperVertical = document.querySelector('.swiper-wrapper[style*="translate3d"]');

        if (wrapper || isFullpage || swiperVertical) {
            result.hijacked = {
                bodyOverflowHidden: bodyHidden,
                htmlOverflowHidden: htmlHidden,
                method: isFullpage ? 'fullpage.js' : swiperVertical ? 'swiper_vertical' : 'custom',
                wrapper: wrapper ? {
                    tag: wrapper.tagName.toLowerCase(),
                    classes: wrapper.className.toString().substring(0, 100),
                    position: getComputedStyle(wrapper).position,
                    transform: getComputedStyle(wrapper).transform
                } : null,
                sectionCount: isFullpage ? fpSections.length : 0
            };
        }
        result.fullpageJs = isFullpage;
    }

    // 2. Scroll snapping
    const allEls = document.querySelectorAll('html, body, body > *, [class*="container"], [class*="wrapper"], main');
    allEls.forEach(el => {
        const cs = getComputedStyle(el);
        if (cs.scrollSnapType && cs.scrollSnapType !== 'none') {
            const children = [];
            el.querySelectorAll(':scope > *').forEach((child, i) => {
                const childCs = getComputedStyle(child);
                if (childCs.scrollSnapAlign && childCs.scrollSnapAlign !== 'none') {
                    children.push({
                        index: i,
                        tag: child.tagName.toLowerCase(),
                        classes: child.className.toString().substring(0, 80),
                        snapAlign: childCs.scrollSnapAlign,
                        snapStop: childCs.scrollSnapStop || 'normal'
                    });
                }
            });
            if (children.length > 0) {
                result.snap = {
                    container: el.tagName.toLowerCase() + (el.className ? '.' + el.className.toString().split(' ')[0] : ''),
                    snapType: cs.scrollSnapType,
                    scrollPadding: cs.scrollPadding !== '0px' ? cs.scrollPadding : null,
                    overscrollBehavior: cs.overscrollBehavior !== 'auto' ? cs.overscrollBehavior : null,
                    children: children.slice(0, 20)
                };
            }
        }
    });

    // 3. Smooth scroll
    result.scrollBehaviorCss = htmlCs.scrollBehavior || bodyCs.scrollBehavior || 'auto';

    // Lenis
    if (window.lenis || window.__lenis) {
        const lenis = window.lenis || window.__lenis;
        result.smoothScroll = {
            library: 'lenis',
            version: lenis.version || null,
            config: {
                duration: lenis.options ? lenis.options.duration : null,
                easing: lenis.options ? (lenis.options.easing ? lenis.options.easing.toString().substring(0, 100) : null) : null,
                smoothWheel: lenis.options ? lenis.options.smoothWheel : null,
                smoothTouch: lenis.options ? lenis.options.smoothTouch : null,
                wheelMultiplier: lenis.options ? lenis.options.wheelMultiplier : null,
                touchMultiplier: lenis.options ? lenis.options.touchMultiplier : null,
                orientation: lenis.options ? lenis.options.orientation : null,
                infinite: lenis.options ? lenis.options.infinite : null,
            }
        };
    }
    // Locomotive Scroll
    else if (window.LocomotiveScroll || document.querySelector('[data-scroll-container]')) {
        const hasSmooth = document.documentElement.classList.contains('has-scroll-smooth');
        result.smoothScroll = {
            library: 'locomotive',
            hasSmooth: hasSmooth,
            dataScrollElements: document.querySelectorAll('[data-scroll]').length,
            dataScrollSpeedElements: document.querySelectorAll('[data-scroll-speed]').length
        };
    }
    // GSAP ScrollSmoother
    else if (window.ScrollSmoother) {
        const sm = window.ScrollSmoother.get ? window.ScrollSmoother.get() : null;
        result.smoothScroll = {
            library: 'gsap_scrollsmoother',
            config: sm ? {
                smooth: sm.vars ? sm.vars.smooth : null,
                effects: sm.vars ? sm.vars.effects : null,
                normalizeScroll: sm.vars ? sm.vars.normalizeScroll : null,
            } : null,
            wrapper: document.querySelector('#smooth-wrapper') ? true : false,
            content: document.querySelector('#smooth-content') ? true : false
        };
    }
    // Lenis detection by class/attribute (if instance not on window)
    else if (document.documentElement.classList.contains('lenis') || document.documentElement.classList.contains('lenis-smooth')) {
        result.smoothScroll = {
            library: 'lenis',
            detectedBy: 'html_class',
            config: null
        };
    }

    // 4. Pinned sections (CSS sticky)
    document.querySelectorAll('body *').forEach(el => {
        const cs = getComputedStyle(el);
        if (cs.position === 'sticky') {
            const parent = el.parentElement;
            const parentRect = parent ? parent.getBoundingClientRect() : { height: 0 };
            const elRect = el.getBoundingClientRect();
            // Only report if parent is significantly taller (means element stays pinned for a while)
            if (parentRect.height > elRect.height * 1.5) {
                result.pinnedSections.push({
                    method: 'css_sticky',
                    element: el.tagName.toLowerCase(),
                    classes: el.className ? el.className.toString().substring(0, 80) : '',
                    id: el.id || '',
                    stickyTop: cs.top,
                    elementHeight: Math.round(elRect.height),
                    parentHeight: Math.round(parentRect.height),
                    pinDuration: Math.round(parentRect.height - elRect.height) + 'px',
                    text: (el.innerText || '').substring(0, 60)
                });
            }
        }
    });

    // GSAP pin-spacers
    document.querySelectorAll('.pin-spacer').forEach(spacer => {
        const pinned = spacer.querySelector(':scope > *');
        result.pinnedSections.push({
            method: 'gsap_pin',
            element: pinned ? pinned.tagName.toLowerCase() : 'unknown',
            classes: pinned ? pinned.className.toString().substring(0, 80) : '',
            id: pinned ? pinned.id : '',
            spacerHeight: Math.round(spacer.getBoundingClientRect().height),
            pinnedHeight: pinned ? Math.round(pinned.getBoundingClientRect().height) : 0,
            text: pinned ? (pinned.innerText || '').substring(0, 60) : ''
        });
    });

    // 5. Parallax data attributes
    const parallaxAttrs = [
        {attr: 'data-scroll-speed', source: 'locomotive'},
        {attr: 'data-speed', source: 'gsap_scrollsmoother'},
        {attr: 'data-lag', source: 'gsap_scrollsmoother'},
        {attr: 'data-rellax-speed', source: 'rellax'},
        {attr: 'data-parallax', source: 'generic'},
        {attr: 'data-parallax-speed', source: 'generic'},
    ];
    parallaxAttrs.forEach(({attr, source}) => {
        document.querySelectorAll(`[${attr}]`).forEach(el => {
            result.parallaxElements.push({
                element: el.tagName.toLowerCase(),
                classes: el.className ? el.className.toString().substring(0, 80) : '',
                id: el.id || '',
                attribute: attr,
                value: el.getAttribute(attr),
                source: source,
                text: (el.innerText || '').substring(0, 40)
            });
        });
    });

    // 6. CSS scroll-timeline
    const sheets = document.styleSheets;
    for (let i = 0; i < sheets.length; i++) {
        try {
            const rules = sheets[i].cssRules || sheets[i].rules;
            for (let j = 0; j < rules.length; j++) {
                const rule = rules[j];
                if (rule.style) {
                    const at = rule.style.animationTimeline;
                    const st = rule.style.scrollTimelineName;
                    const vt = rule.style.viewTimelineName;
                    if ((at && at !== 'auto') || st || vt) {
                        result.cssScrollTimeline.push({
                            selector: rule.selectorText || '',
                            animationTimeline: at || null,
                            scrollTimelineName: st || null,
                            viewTimelineName: vt || null,
                            animationRange: rule.style.animationRange || null,
                            animationName: rule.style.animationName || null,
                        });
                    }
                }
            }
        } catch (e) { /* CORS */ }
    }

    return result;
}
"""

EXTRACT_MOUSE_EFFECTS_JS = """
() => {
    const result = {
        cursorFollower: null,
        tiltCards: [],
        magneticButtons: [],
        backgroundParallax: [],
        css3dParallax: [],
        libraries: {}
    };

    // 1. Custom cursor detection
    const htmlCs = getComputedStyle(document.documentElement);
    const bodyCs = getComputedStyle(document.body);
    const hideCursor = htmlCs.cursor === 'none' || bodyCs.cursor === 'none';

    // Find cursor follower elements (fixed, small, round, pointer-events:none)
    const cursorCandidates = [];
    document.querySelectorAll('body *').forEach(el => {
        const cs = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        if (cs.position === 'fixed' && cs.pointerEvents === 'none' && rect.width < 80 && rect.width > 3 && rect.height < 80 && rect.height > 3) {
            cursorCandidates.push({
                element: el.tagName.toLowerCase(),
                classes: el.className ? el.className.toString().substring(0, 80) : '',
                id: el.id || '',
                width: Math.round(rect.width),
                height: Math.round(rect.height),
                borderRadius: cs.borderRadius,
                blendMode: cs.mixBlendMode !== 'normal' ? cs.mixBlendMode : null,
                zIndex: cs.zIndex,
                backgroundColor: cs.backgroundColor,
            });
        }
    });

    if (cursorCandidates.length > 0 || hideCursor) {
        result.cursorFollower = {
            hideDefaultCursor: hideCursor,
            cursorCssOnHtml: htmlCs.cursor,
            cursorCssOnBody: bodyCs.cursor,
            elements: cursorCandidates
        };
    }

    // 2. Tilt / perspective cards
    document.querySelectorAll('body *').forEach(el => {
        const cs = getComputedStyle(el);
        if (cs.perspective && cs.perspective !== 'none') {
            const children = [];
            el.querySelectorAll(':scope > *').forEach(child => {
                const childCs = getComputedStyle(child);
                if (childCs.transformStyle === 'preserve-3d' || (childCs.transform && childCs.transform.includes('rotate'))) {
                    children.push({
                        element: child.tagName.toLowerCase(),
                        classes: child.className ? child.className.toString().substring(0, 80) : '',
                        transform: childCs.transform,
                        transformStyle: childCs.transformStyle,
                    });
                }
            });
            if (children.length > 0) {
                result.tiltCards.push({
                    container: el.tagName.toLowerCase(),
                    classes: el.className ? el.className.toString().substring(0, 80) : '',
                    perspective: cs.perspective,
                    children: children.slice(0, 5)
                });
            }
        }
    });

    // Vanilla Tilt / Atropos detection
    result.libraries.vanillaTilt = !!window.VanillaTilt;
    result.libraries.atropos = !!window.Atropos;
    result.libraries.rellax = !!window.Rellax;
    result.libraries.simpleParallax = !!window.simpleParallax;

    // data-tilt attributes
    document.querySelectorAll('[data-tilt]').forEach(el => {
        result.tiltCards.push({
            container: el.tagName.toLowerCase(),
            classes: el.className ? el.className.toString().substring(0, 80) : '',
            library: 'vanilla-tilt',
            maxRotation: el.getAttribute('data-tilt-max') || '20',
            speed: el.getAttribute('data-tilt-speed') || '400',
            glare: el.getAttribute('data-tilt-glare') || 'false',
            glareMaxOpacity: el.getAttribute('data-tilt-max-glare') || '0.5',
            perspective: el.getAttribute('data-tilt-perspective') || '1000',
            text: (el.innerText || '').substring(0, 40)
        });
    });

    // 3. Background parallax (CSS)
    document.querySelectorAll('body *').forEach(el => {
        const cs = getComputedStyle(el);
        if (cs.backgroundAttachment === 'fixed') {
            result.backgroundParallax.push({
                element: el.tagName.toLowerCase(),
                classes: el.className ? el.className.toString().substring(0, 80) : '',
                id: el.id || '',
                backgroundImage: cs.backgroundImage.substring(0, 120),
                backgroundSize: cs.backgroundSize,
            });
        }
    });

    // 4. CSS 3D parallax (perspective + translateZ on children)
    document.querySelectorAll('body *').forEach(el => {
        const cs = getComputedStyle(el);
        if (cs.perspective && cs.perspective !== 'none') {
            const layers = [];
            el.querySelectorAll(':scope *').forEach(child => {
                const childCs = getComputedStyle(child);
                if (childCs.transform && childCs.transform.includes('matrix3d')) {
                    layers.push({
                        element: child.tagName.toLowerCase(),
                        classes: child.className ? child.className.toString().substring(0, 80) : '',
                        transform: childCs.transform,
                    });
                }
            });
            if (layers.length > 0) {
                result.css3dParallax.push({
                    container: el.tagName.toLowerCase(),
                    classes: el.className ? el.className.toString().substring(0, 80) : '',
                    perspective: cs.perspective,
                    layers: layers.slice(0, 10)
                });
            }
        }
    });

    return result;
}
"""

EXTRACT_GSAP_SCROLLTRIGGER_JS = """
() => {
    const result = {
        available: false,
        triggers: [],
        pinSpacers: [],
        scrollSmootherConfig: null
    };

    // Check if GSAP ScrollTrigger is available
    if (!window.ScrollTrigger && !(window.gsap && window.gsap.plugins)) {
        return result;
    }

    result.available = true;

    // Get all ScrollTrigger instances
    try {
        const allTriggers = window.ScrollTrigger.getAll ? window.ScrollTrigger.getAll() : [];

        allTriggers.forEach((st, i) => {
            const vars = st.vars || {};
            const trigger = st.trigger;

            result.triggers.push({
                index: i,
                triggerElement: trigger ? trigger.tagName.toLowerCase() : null,
                triggerClasses: trigger && trigger.className ? trigger.className.toString().substring(0, 80) : '',
                triggerId: trigger ? trigger.id || '' : '',
                triggerText: trigger ? (trigger.innerText || '').substring(0, 40) : '',
                start: vars.start || 'top bottom',
                end: vars.end || 'bottom top',
                scrub: vars.scrub !== undefined ? vars.scrub : false,
                pin: !!vars.pin,
                pinSpacing: vars.pinSpacing !== undefined ? vars.pinSpacing : true,
                snap: vars.snap || null,
                markers: !!vars.markers,
                toggleActions: vars.toggleActions || null,
                toggleClass: vars.toggleClass || null,
                once: !!vars.once,
                // Animation details if available
                animation: st.animation ? {
                    duration: st.animation.duration ? st.animation.duration() : null,
                    vars: st.animation.vars ? {
                        from: st.animation.vars.startAt || null,
                        to: (() => {
                            const v = {...st.animation.vars};
                            delete v.startAt; delete v.scrollTrigger; delete v.ease;
                            return Object.keys(v).length > 0 ? v : null;
                        })()
                    } : null
                } : null
            });
        });
    } catch (e) {}

    // Pin spacers
    document.querySelectorAll('.pin-spacer').forEach(spacer => {
        const pinned = spacer.querySelector(':scope > *');
        result.pinSpacers.push({
            spacerClasses: spacer.className.toString().substring(0, 80),
            spacerHeight: Math.round(spacer.getBoundingClientRect().height),
            pinnedElement: pinned ? pinned.tagName.toLowerCase() : null,
            pinnedClasses: pinned ? pinned.className.toString().substring(0, 80) : '',
            pinnedId: pinned ? pinned.id || '' : '',
        });
    });

    // ScrollSmoother config
    try {
        if (window.ScrollSmoother && window.ScrollSmoother.get) {
            const sm = window.ScrollSmoother.get();
            if (sm) {
                result.scrollSmootherConfig = {
                    smooth: sm.vars ? sm.vars.smooth : null,
                    effects: sm.vars ? sm.vars.effects : null,
                    normalizeScroll: sm.vars ? sm.vars.normalizeScroll : null,
                    smoothTouch: sm.vars ? sm.vars.smoothTouch : null,
                    speed: sm.vars ? sm.vars.speed : null,
                };
            }
        }
    } catch (e) {}

    return result;
}
"""


async def simulate_mouse_effects(page):
    """Simulate mouse movement and detect dynamic effects (parallax, cursor follower, tilt)."""
    log("  Simulating mouse effects (CDP mouseMoved)...")

    try:
        cdp = await page.context.new_cdp_session(page)

        # Ensure we're at the top and capture initial state of interesting elements
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        # Capture initial transforms of all visible elements that might react to mouse
        CAPTURE_MOUSE_TARGETS_JS = """
        () => {
            const targets = [];
            const selectors = 'body > *, header *, [class*="hero"] *, [class*="card"], [data-tilt], [class*="parallax"] *, nav *, a, button';
            const els = document.querySelectorAll(selectors);
            const seen = new Set();
            const maxEls = Math.min(els.length, 100);

            for (let i = 0; i < maxEls; i++) {
                const el = els[i];
                const rect = el.getBoundingClientRect();
                if (rect.width < 5 || rect.height < 5 || rect.top > window.innerHeight * 1.2) continue;

                const cs = getComputedStyle(el);
                const key = el.tagName + '|' + (el.className || '').toString().substring(0, 40);
                if (seen.has(key)) continue;
                seen.add(key);

                targets.push({
                    index: targets.length,
                    element: el.tagName.toLowerCase(),
                    classes: el.className ? el.className.toString().substring(0, 80) : '',
                    id: el.id || '',
                    transform: cs.transform,
                    left: cs.left,
                    top: cs.top,
                    opacity: cs.opacity,
                    position: cs.position,
                    pointerEvents: cs.pointerEvents,
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                });
            }
            return targets;
        }
        """

        before_state = await page.evaluate(CAPTURE_MOUSE_TARGETS_JS)

        # Move mouse to center then to corners to detect parallax/tracking
        positions = [
            (960, 540),   # center
            (100, 100),   # top-left
            (1820, 100),  # top-right
            (100, 980),   # bottom-left
            (1820, 980),  # bottom-right
            (960, 200),   # top-center
            (960, 880),   # bottom-center
        ]

        mouse_snapshots = []

        for x, y in positions:
            await cdp.send("Input.dispatchMouseEvent", {
                "type": "mouseMoved",
                "x": x,
                "y": y,
            })
            await page.wait_for_timeout(200)

            # Capture state after mouse move
            after = await page.evaluate(CAPTURE_MOUSE_TARGETS_JS)
            mouse_snapshots.append({"mouseX": x, "mouseY": y, "states": after})

        await cdp.detach()

        # Compare: find elements whose transform/position changed with mouse position
        diffs = []
        if before_state and len(mouse_snapshots) >= 3:
            for i, before_el in enumerate(before_state):
                changes_at_positions = []

                for snap in mouse_snapshots:
                    after_els = snap["states"]
                    if i >= len(after_els):
                        continue
                    after_el = after_els[i]

                    # Check if transform or position changed
                    changed_props = {}
                    for prop in ["transform", "left", "top", "opacity"]:
                        if before_el.get(prop) != after_el.get(prop):
                            changed_props[prop] = {"from": before_el.get(prop), "to": after_el.get(prop)}

                    if changed_props:
                        changes_at_positions.append({
                            "mouseX": snap["mouseX"],
                            "mouseY": snap["mouseY"],
                            "changes": changed_props
                        })

                if changes_at_positions:
                    # Classify the effect
                    effect_type = "unknown"
                    el = before_el
                    if el.get("position") == "fixed" and el.get("pointerEvents") == "none" and el.get("width", 100) < 80:
                        effect_type = "cursor_follower"
                    elif any("transform" in c.get("changes", {}) for c in changes_at_positions):
                        effect_type = "mouse_parallax" if len(changes_at_positions) >= 3 else "mouse_reactive"

                    diffs.append({
                        "element": el.get("element"),
                        "classes": el.get("classes"),
                        "id": el.get("id"),
                        "effectType": effect_type,
                        "positions": changes_at_positions[:5]
                    })

        log(f"    Mouse effect diffs: {len(diffs)} elements react to mouse movement")
        return diffs

    except Exception as e:
        log(f"    Mouse simulation failed: {e}")
        return []


async def detect_scroll_parallax(page):
    """Detect parallax by comparing element movement ratios during scroll."""
    log("  Detecting parallax layers via scroll ratio analysis...")

    try:
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        # Capture positions of many elements at scrollY=0
        CAPTURE_POSITIONS_JS = """
        () => {
            const els = document.querySelectorAll('body > *, body > * > *, section > *, header > *, [class*="hero"] > *, [class*="parallax"], img, video, [style*="background"]');
            const result = [];
            const seen = new Set();
            const max = Math.min(els.length, 80);

            for (let i = 0; i < max; i++) {
                const el = els[i];
                const tag = el.tagName.toLowerCase();
                if (['script', 'style', 'noscript', 'link', 'meta', 'br'].includes(tag)) continue;

                const rect = el.getBoundingClientRect();
                if (rect.width < 10 || rect.height < 10) continue;

                const key = tag + '|' + (el.className || '').toString().substring(0, 50) + '|' + Math.round(rect.top);
                if (seen.has(key)) continue;
                seen.add(key);

                const cs = getComputedStyle(el);
                result.push({
                    index: result.length,
                    element: tag,
                    classes: el.className ? el.className.toString().substring(0, 80) : '',
                    id: el.id || '',
                    top: rect.top,
                    left: rect.left,
                    height: rect.height,
                    width: rect.width,
                    transform: cs.transform,
                    position: cs.position,
                    bgAttachment: cs.backgroundAttachment,
                    text: (el.innerText || '').substring(0, 30)
                });
            }
            return result;
        }
        """

        pos_at_0 = await page.evaluate(CAPTURE_POSITIONS_JS)

        # Scroll to 1 viewport height
        viewport_h = await page.evaluate("window.innerHeight")
        await page.evaluate(f"window.scrollTo({{top: {viewport_h}, behavior: 'instant'}})")
        await page.wait_for_timeout(600)

        pos_at_vh = await page.evaluate(CAPTURE_POSITIONS_JS)

        # Scroll back
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)

        # Compare: normal elements move by -viewport_h, parallax elements move differently
        layers = []
        scroll_delta = viewport_h

        for i, el0 in enumerate(pos_at_0):
            # Find matching element in second snapshot
            match = None
            for el1 in pos_at_vh:
                if el0.get("element") == el1.get("element") and el0.get("classes") == el1.get("classes") and el0.get("id") == el1.get("id"):
                    match = el1
                    break

            if not match:
                continue

            # Calculate movement
            movement = match["top"] - el0["top"]
            expected_movement = -scroll_delta  # normal elements move up by scroll amount

            # Skip fixed/sticky elements (they don't move or move differently by design)
            if el0.get("position") in ("fixed", "sticky"):
                continue

            # Calculate speed ratio: 1.0 = normal, < 1.0 = slower (background parallax), > 1.0 = faster (foreground)
            if abs(expected_movement) > 10:
                speed_ratio = round(movement / expected_movement, 3)

                # Parallax: anything that moves at a different rate than normal scroll
                if abs(speed_ratio - 1.0) > 0.05 and abs(speed_ratio) < 5.0:
                    layers.append({
                        "element": el0.get("element"),
                        "classes": el0.get("classes"),
                        "id": el0.get("id"),
                        "text": el0.get("text"),
                        "speedRatio": speed_ratio,
                        "actualMovement": round(movement, 1),
                        "expectedMovement": round(expected_movement, 1),
                        "classification": "slower_background" if speed_ratio < 1.0 else "faster_foreground",
                        "bgAttachment": el0.get("bgAttachment"),
                    })

        log(f"    Parallax layers detected: {len(layers)}")
        return {"scrollDelta": scroll_delta, "layers": layers}

    except Exception as e:
        log(f"    Parallax detection failed: {e}")
        return {"scrollDelta": 0, "layers": []}


async def extract_design_data(page):
    """Run all JS extraction functions on the page."""
    log("  Extracting design tokens...")
    tokens = await page.evaluate(EXTRACT_DESIGN_TOKENS_JS)

    log("  Extracting animations...")
    animations = await page.evaluate(EXTRACT_ANIMATIONS_JS)

    log("  Extracting layout...")
    layout = await page.evaluate(EXTRACT_LAYOUT_JS)

    return {
        "tokens": tokens,
        "animations": animations,
        "layout": layout
    }


async def record_scroll_animations(page):
    """Record scroll-triggered animations using CDP real wheel events + before/after comparison.

    Strategy:
    1. Capture BEFORE states (page at top, elements not yet triggered)
    2. Use CDP Input.dispatchMouseEvent (wheel) for REAL scroll that triggers IntersectionObserver
    3. Also use CDP Animation.enable to intercept animations as they fire
    4. Capture AFTER states and compare
    5. Capture runtime Web Animations at multiple scroll positions
    """
    log("  Recording scroll animation states (CDP approach)...")

    try:
        # Ensure we're at the very top
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(1000)

        # 1. Capture BEFORE states (elements not yet animated)
        before_states = await page.evaluate(CAPTURE_ELEMENT_STATES_JS)
        log(f"    Tracking {len(before_states)} elements with appear/animation attributes")

        if len(before_states) == 0:
            log("    No animated elements found")
            return {"beforeAfter": [], "runtimeAnimations": []}

        # 2. Set up CDP session for real scroll events + animation interception
        cdp = await page.context.new_cdp_session(page)

        # Enable Animation domain to intercept animations as they fire
        cdp_animations = []
        await cdp.send("Animation.enable")

        async def resolve_node_info(backend_node_id):
            """Try to resolve a backendNodeId to useful element info."""
            try:
                result = await cdp.send("DOM.describeNode", {"backendNodeId": backend_node_id})
                node = result.get("node", {})
                attrs = node.get("attributes", [])
                attr_dict = {}
                for k in range(0, len(attrs), 2):
                    attr_dict[attrs[k]] = attrs[k+1] if k+1 < len(attrs) else ""
                return {
                    "nodeName": node.get("nodeName", ""),
                    "nodeId": node.get("nodeId", 0),
                    "classes": attr_dict.get("class", "")[:80],
                    "id": attr_dict.get("id", ""),
                    "appearId": attr_dict.get("data-framer-appear-id", ""),
                }
            except Exception:
                return {"nodeName": "unknown", "nodeId": 0}

        def on_animation_started(params):
            anim = params.get("animation", {})
            source = anim.get("source", {})
            cdp_animations.append({
                "id": anim.get("id", ""),
                "name": anim.get("name", ""),
                "type": anim.get("type", ""),
                "duration": source.get("duration", 0),
                "delay": source.get("delay", 0),
                "easing": source.get("easing", ""),
                "backendNodeId": source.get("backendNodeId", 0),
                "iterations": source.get("iterations", 1),
                "direction": source.get("direction", "normal"),
                "fill": source.get("fill", "auto"),
                "keyframesRule": source.get("keyframesRule", {}),
                "cssId": anim.get("cssId", ""),
            })

        cdp.on("Animation.animationStarted", on_animation_started)

        # 3. Scroll down using REAL mouse wheel events via CDP
        # These trigger IntersectionObserver unlike programmatic scrollTo
        total_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = await page.evaluate("window.innerHeight")
        current_scroll = 0
        scroll_step = 200  # pixels per wheel event (smaller = more triggers)
        runtime_animations_all = []

        log(f"    Page height: {total_height}px, scrolling with CDP wheel events...")

        # Use actual scroll position tracking instead of estimated counter
        stalled_count = 0
        last_actual = 0

        while True:
            # Dispatch a real mouse wheel event at center of viewport
            await cdp.send("Input.dispatchMouseEvent", {
                "type": "mouseWheel",
                "x": 960,  # center of 1920 viewport
                "y": 540,  # center of 1080 viewport
                "deltaX": 0,
                "deltaY": scroll_step,
            })
            await page.wait_for_timeout(100)

            # Check actual position
            actual_scroll = await page.evaluate("window.scrollY")

            # If CDP wheel isn't scrolling fast enough, force it via JS
            if actual_scroll < last_actual + scroll_step * 0.5:
                target = min(last_actual + scroll_step, total_height)
                await page.evaluate(f"window.scrollTo({{top: {target}, behavior: 'instant'}})")
                await page.wait_for_timeout(100)
                actual_scroll = await page.evaluate("window.scrollY")

            # Detect stall (reached bottom or page won't scroll further)
            if abs(actual_scroll - last_actual) < 10:
                stalled_count += 1
                if stalled_count > 5:
                    break
            else:
                stalled_count = 0

            last_actual = actual_scroll
            current_scroll = actual_scroll

            # Every ~400px, capture runtime animations snapshot
            # This catches Framer appear animations as they fire during scroll
            if int(current_scroll) % 400 < scroll_step:
                try:
                    rt_anims = await page.evaluate(CAPTURE_RUNTIME_ANIMATIONS_JS)
                    if rt_anims:
                        for anim in rt_anims:
                            anim["capturedAtScroll"] = int(current_scroll)
                        runtime_animations_all.extend(rt_anims)
                except Exception:
                    pass

            if actual_scroll >= total_height - viewport_height:
                break

        log(f"    Scroll completed at position: {int(last_actual)}px")

        # Pause to let final animations finish
        await page.wait_for_timeout(2500)

        # 4. Capture AFTER states (elements should be in their animated/final state)
        after_states = await page.evaluate(CAPTURE_ELEMENT_STATES_JS)

        # Capture final runtime animations too
        try:
            final_rt = await page.evaluate(CAPTURE_RUNTIME_ANIMATIONS_JS)
            if final_rt:
                for anim in final_rt:
                    anim["capturedAtScroll"] = "final"
                runtime_animations_all.extend(final_rt)
        except Exception:
            pass

        # Resolve CDP animation node info (requires DOM domain)
        try:
            await cdp.send("DOM.enable")
            # Get document first to populate DOM tree
            await cdp.send("DOM.getDocument", {"depth": 0})
            for anim_info in cdp_animations:
                node_id = anim_info.get("backendNodeId", 0)
                if node_id > 0:
                    node_info = await resolve_node_info(node_id)
                    anim_info["nodeInfo"] = node_info
            await cdp.send("DOM.disable")
        except Exception as e:
            log(f"    CDP node resolution failed: {e}")

        # Cleanup CDP
        await cdp.send("Animation.disable")
        await cdp.detach()

        # 5. Compare BEFORE vs AFTER
        before_after = []
        for i, before in enumerate(before_states):
            after = after_states[i] if i < len(after_states) else None
            if not after:
                continue

            bs = before.get("state", {})
            as_ = after.get("state", {})

            # Detect what changed (computed + inline styles)
            changes = {}
            for prop in ["opacity", "transform", "visibility", "clipPath", "filter", "translate", "scale", "rotate", "inlineOpacity", "inlineTransform"]:
                bv = bs.get(prop, "")
                av = as_.get(prop, "")
                if bv != av:
                    changes[prop] = {"from": bv, "to": av}

            if changes:
                before_after.append({
                    "element": before.get("element", ""),
                    "classes": before.get("classes", ""),
                    "id": before.get("id", ""),
                    "text": before.get("text", ""),
                    "childHeading": before.get("childHeading", ""),
                    "appearId": before.get("appearId", ""),
                    "framerType": before.get("framerType", ""),
                    "absoluteTop": before.get("absoluteTop", 0),
                    "changes": changes
                })

        # 6. Deduplicate runtime animations by element+keyframes
        seen_rt = set()
        unique_rt = []
        for anim in runtime_animations_all:
            key = f"{anim.get('element','')}|{anim.get('classes','')}|{anim.get('appearId','')}"
            if key not in seen_rt:
                seen_rt.add(key)
                unique_rt.append(anim)

        log(f"    Before/After diffs: {len(before_after)} elements changed")
        log(f"    CDP animations intercepted: {len(cdp_animations)}")
        log(f"    Runtime animations captured: {len(unique_rt)}")

        return {
            "beforeAfter": before_after,
            "cdpAnimations": cdp_animations,
            "runtimeAnimations": unique_rt
        }

    except Exception as e:
        log(f"    Failed to record scroll animations: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {"beforeAfter": [], "cdpAnimations": [], "runtimeAnimations": []}


async def capture_hover_states(page, output_dir):
    """Hover over interactive elements and capture before/after screenshots."""
    log("  Capturing hover state diffs...")
    screenshots_dir = os.path.join(output_dir, 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)

    hover_data = []
    selectors = 'a[href], button, [role="button"], .hover, [class*="card"], [class*="btn"]'

    try:
        # Get elements info first
        elements_info = await page.evaluate(CAPTURE_HOVER_DIFFS_JS, selectors)

        # Hover over each and take before/after screenshot
        locators = page.locator(selectors)
        count = min(await locators.count(), 15)

        for i in range(count):
            try:
                loc = locators.nth(i)
                if not await loc.is_visible():
                    continue

                # Scroll to element
                await loc.scroll_into_view_if_needed()
                await page.wait_for_timeout(200)

                # Screenshot before hover
                before_path = os.path.join(screenshots_dir, f"hover-{i:02d}-before.png")
                await loc.screenshot(path=before_path)

                # Hover
                await loc.hover()
                await page.wait_for_timeout(400)

                # Capture hover computed style
                hover_style = await page.evaluate("""
                    (idx) => {
                        const els = document.querySelectorAll('a[href], button, [role="button"], .hover, [class*="card"], [class*="btn"]');
                        const el = els[idx];
                        if (!el) return null;
                        const cs = getComputedStyle(el);
                        return {
                            transform: cs.transform,
                            backgroundColor: cs.backgroundColor,
                            color: cs.color,
                            boxShadow: cs.boxShadow,
                            borderColor: cs.borderTopColor,
                            opacity: cs.opacity,
                            scale: cs.scale,
                            filter: cs.filter
                        };
                    }
                """, i)

                # Screenshot after hover
                after_path = os.path.join(screenshots_dir, f"hover-{i:02d}-after.png")
                await loc.screenshot(path=after_path)

                if i < len(elements_info) and hover_style:
                    info = elements_info[i]
                    # Check if anything actually changed
                    normal = info.get('normalState', {})
                    changed = {}
                    for key in hover_style:
                        if hover_style[key] != normal.get(key):
                            changed[key] = {'from': normal.get(key, ''), 'to': hover_style[key]}

                    if changed:
                        hover_data.append({
                            'element': info.get('element', ''),
                            'classes': info.get('classes', ''),
                            'text': info.get('text', ''),
                            'changes': changed,
                            'screenshotBefore': f"hover-{i:02d}-before.png",
                            'screenshotAfter': f"hover-{i:02d}-after.png"
                        })
                        log(f"    Hover diff #{i}: {len(changed)} properties changed")

                # Move mouse away
                await page.mouse.move(0, 0)
                await page.wait_for_timeout(200)

            except Exception as e:
                pass  # Some elements may not be hoverable

    except Exception as e:
        log(f"    Hover capture failed: {e}")

    log(f"    Total hover diffs captured: {len(hover_data)}")
    return hover_data


async def download_videos(page, videos, output_dir):
    """Download embedded videos from the page."""
    video_dir = os.path.join(output_dir, 'video')
    os.makedirs(video_dir, exist_ok=True)
    downloaded = []

    for i, video in enumerate(videos):
        src = video.get('src', '')
        if not src or src.startswith('blob:'):
            continue

        try:
            response = await page.request.get(src, timeout=30000)
            if response.ok:
                body = await response.body()
                ext = '.mp4'
                if '.webm' in src:
                    ext = '.webm'
                elif '.mov' in src:
                    ext = '.mov'
                filename = f"embedded-video-{i:02d}{ext}"
                filepath = os.path.join(video_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(body)
                downloaded.append(filename)
                size_mb = len(body) / 1024 / 1024
                log(f"    Downloaded video: {filename} ({size_mb:.1f}MB)")
        except Exception as e:
            log(f"    Failed to download video {src[:60]}: {e}")

    return downloaded


async def capture_section_screenshots(page, sections, output_dir):
    """Take screenshots of individual sections by scrolling to each one."""
    screenshots_dir = os.path.join(output_dir, 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    captured = []

    # First take a full-page screenshot, then crop sections from it
    # This avoids the clip-outside-viewport issue
    import tempfile
    full_tmp = os.path.join(screenshots_dir, '_full_tmp.png')

    try:
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=full_tmp, full_page=True)
    except Exception as e:
        log(f"    Failed to capture full-page for sectioning: {e}")
        return captured

    # Use PIL if available, otherwise fall back to scroll-and-capture
    try:
        from PIL import Image
        full_img = Image.open(full_tmp)
        full_width, full_height = full_img.size

        for section in sections:
            idx = section['index']
            label = re.sub(r'[^\w\s-]', '', section.get('label', f'section-{idx}'))
            label = re.sub(r'\s+', '-', label).lower()[:40]
            filename = f"section-{idx:03d}-{label}.png"
            filepath = os.path.join(screenshots_dir, filename)

            top = section.get('top', 0)
            height = section.get('height', 0)
            width = section.get('width', full_width)

            if height < 20:
                continue

            # Scale factor: full-page screenshot may differ from CSS pixels
            scale = full_width / 1920 if full_width > 1920 else 1

            crop_top = int(top * scale)
            crop_bottom = min(int((top + height) * scale), full_height)
            crop_right = min(int(width * scale), full_width)

            if crop_bottom <= crop_top:
                continue

            try:
                cropped = full_img.crop((0, crop_top, crop_right, crop_bottom))
                cropped.save(filepath)
                captured.append(filename)
                log(f"    Screenshot: {filename} ({width}x{height})")
            except Exception as e:
                log(f"    Failed crop section {idx}: {e}")

        full_img.close()

    except ImportError:
        # PIL not available — fallback to scroll-and-viewport-capture
        log("    PIL not available, using scroll-capture fallback")
        for section in sections:
            idx = section['index']
            label = re.sub(r'[^\w\s-]', '', section.get('label', f'section-{idx}'))
            label = re.sub(r'\s+', '-', label).lower()[:40]
            filename = f"section-{idx:03d}-{label}.png"
            filepath = os.path.join(screenshots_dir, filename)

            top = section.get('top', 0)
            height = section.get('height', 0)

            if height < 20:
                continue

            try:
                await page.evaluate(f"window.scrollTo(0, {max(0, top - 10)})")
                await page.wait_for_timeout(400)
                await page.screenshot(path=filepath)
                captured.append(filename)
                log(f"    Screenshot: {filename} (viewport at y={top})")
            except Exception as e:
                log(f"    Failed screenshot section {idx}: {e}")

    # Cleanup temp file
    if os.path.exists(full_tmp):
        os.remove(full_tmp)

    return captured


async def capture_full_page_screenshots(page, output_dir, viewports):
    """Take full-page screenshots at different viewport widths."""
    screenshots_dir = os.path.join(output_dir, 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    captured = []

    for name, width in viewports:
        filename = f"full-page-{name}.png"
        filepath = os.path.join(screenshots_dir, filename)

        try:
            await page.set_viewport_size({"width": width, "height": 1080})
            await page.wait_for_timeout(1500)

            # Scroll to bottom to trigger lazy load, then back to top
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(500)

            await page.screenshot(path=filepath, full_page=True)
            captured.append(filename)
            log(f"    Full-page screenshot: {filename} (width={width})")
        except Exception as e:
            log(f"    Failed full-page screenshot {name}: {e}")

    return captured


async def capture_scroll_video(url, output_dir):
    """Record a video of scrolling through the page."""
    from playwright.async_api import async_playwright
    from playwright_stealth import Stealth

    video_dir = os.path.join(output_dir, 'video')
    os.makedirs(video_dir, exist_ok=True)

    log("  Recording scroll video...")

    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            record_video_dir=video_dir,
            record_video_size={"width": 1920, "height": 1080},
        )

        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Pause at top
        await page.wait_for_timeout(2000)

        # Smooth scroll down
        total_height = await page.evaluate("document.body.scrollHeight")
        current = 0
        step = 120
        while current < total_height:
            await page.evaluate(f"window.scrollTo({{top: {current}, behavior: 'instant'}})")
            await page.wait_for_timeout(100)
            current += step

        # Pause at bottom
        await page.wait_for_timeout(2000)

        # Scroll back up
        await page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
        await page.wait_for_timeout(1500)

        video = page.video
        await context.close()
        await browser.close()

        if video:
            video_path = await video.path()
            final_path = os.path.join(video_dir, 'scroll-desktop.webm')
            if os.path.exists(video_path) and video_path != final_path:
                os.rename(video_path, final_path)
            log(f"    Video saved: scroll-desktop.webm")
            return 'video/scroll-desktop.webm'

    return None


async def scrape_design(url, output_dir, record_video=False, responsive=False):
    """Main function: extract design system from a URL."""
    from playwright.async_api import async_playwright
    from playwright_stealth import Stealth

    os.makedirs(output_dir, exist_ok=True)

    log(f"Starting design extraction: {url}")
    log(f"Output: {output_dir}")
    log(f"Video: {record_video}, Responsive: {responsive}")

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

        log("  Loading page...")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # === PHASE 1: Static analysis (BEFORE any scrolling) ===
        log("  Extracting scroll behavior (static)...")
        scroll_behavior = await page.evaluate(EXTRACT_SCROLL_BEHAVIOR_JS)

        log("  Extracting mouse effects (static)...")
        mouse_effects_static = await page.evaluate(EXTRACT_MOUSE_EFFECTS_JS)

        # === PHASE 2: Scroll animations (one-shot triggers) ===
        # IMPORTANT: Record scroll animations BEFORE any other scrolling
        # Framer appear animations are one-shot — they only trigger once
        # when elements first enter the viewport
        scroll_animations = await record_scroll_animations(page)

        # === PHASE 3: Dynamic interaction analysis ===
        # Mouse effects (CDP mouseMoved simulation)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        mouse_diffs = await simulate_mouse_effects(page)

        # Parallax detection (scroll ratio comparison)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        parallax_data = await detect_scroll_parallax(page)

        # Now scroll to trigger lazy loading for the rest of the extraction
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        for i in range(3):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        # === PHASE 4: Design data extraction ===
        design_data = await extract_design_data(page)

        # Convert raw colors to hex
        for color_entry in design_data['tokens'].get('colors', []):
            color_entry['hex'] = rgb_to_hex(color_entry['raw'])

        # Attach scroll animations
        design_data['animations']['scrollAnimationRecording'] = scroll_animations

        # GSAP ScrollTrigger extraction (if detected)
        gsap_data = {"available": False, "triggers": [], "pinSpacers": []}
        if design_data['animations'].get('jsLibraries', {}).get('gsap') or design_data['animations'].get('jsLibraries', {}).get('scrollTrigger'):
            log("  Extracting GSAP ScrollTrigger config...")
            gsap_data = await page.evaluate(EXTRACT_GSAP_SCROLLTRIGGER_JS)

        # Build interactions object
        design_data['interactions'] = {
            'scrollBehavior': scroll_behavior,
            'mouseEffects': {
                **mouse_effects_static,
                'dynamicDiffs': mouse_diffs
            },
            'gsapScrollTrigger': gsap_data,
            'parallax': parallax_data,
        }

        # Capture hover state diffs
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        hover_diffs = await capture_hover_states(page, output_dir)
        design_data['animations']['hoverDiffs'] = hover_diffs

        # Download embedded videos
        videos = design_data['animations'].get('videos', [])
        if videos:
            downloaded_vids = await download_videos(page, videos, output_dir)
            design_data['animations']['downloadedVideos'] = downloaded_vids

        # Screenshots per section
        log("  Capturing section screenshots...")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        sections = design_data['layout'].get('sections', [])
        section_screenshots = await capture_section_screenshots(page, sections, output_dir)

        # Full-page screenshots
        log("  Capturing full-page screenshots...")
        viewports = [("desktop", 1920)]
        if responsive:
            viewports.extend([("tablet", 768), ("mobile", 375)])
        full_screenshots = await capture_full_page_screenshots(page, output_dir, viewports)

        await browser.close()

    # Video (separate browser instance with recording context)
    video_path = None
    if record_video:
        video_path = await capture_scroll_video(url, output_dir)

    # Build final output
    design_data['metadata'] = {
        'url': url,
        'domain': urlparse(url).netloc,
        'screenshots': {
            'sections': section_screenshots,
            'fullPage': full_screenshots
        },
        'video': video_path
    }

    # Save design-data.json
    data_path = os.path.join(output_dir, 'design-data.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(design_data, f, ensure_ascii=False, indent=2)

    # Summary
    token_count = len(design_data['tokens'].get('colors', []))
    font_count = len(design_data['tokens'].get('typography', []))
    anim_count = len(design_data['animations'].get('cssAnimations', []))
    trans_count = len(design_data['animations'].get('cssTransitions', []))
    kf_count = len(design_data['animations'].get('keyframes', []))
    web_anim_count = len(design_data['animations'].get('webAnimations', []))
    scroll_rec = design_data['animations'].get('scrollAnimationRecording', {})
    scroll_ba_count = len(scroll_rec.get('beforeAfter', []))
    scroll_cdp_count = len(scroll_rec.get('cdpAnimations', []))
    scroll_rt_count = len(scroll_rec.get('runtimeAnimations', []))
    hover_diff_count = len(design_data['animations'].get('hoverDiffs', []))
    video_count = len(design_data['animations'].get('videos', []))
    section_count = len(sections)
    libs_detected = [k for k, v in design_data['animations'].get('jsLibraries', {}).items() if v is True or (isinstance(v, str) and v)]

    # Interaction counts
    interactions = design_data.get('interactions', {})
    sb = interactions.get('scrollBehavior', {})
    scroll_hijacked = bool(sb.get('hijacked'))
    scroll_snap_detected = bool(sb.get('snap'))
    smooth_scroll_lib = sb.get('smoothScroll', {}).get('library', None) if sb.get('smoothScroll') else None
    pinned_count = len(sb.get('pinnedSections', []))
    parallax_attr_count = len(sb.get('parallaxElements', []))
    css_scroll_timeline_count = len(sb.get('cssScrollTimeline', []))
    me = interactions.get('mouseEffects', {})
    cursor_follower = bool(me.get('cursorFollower'))
    tilt_count = len(me.get('tiltCards', []))
    mouse_dynamic_count = len(me.get('dynamicDiffs', []))
    bg_parallax_count = len(me.get('backgroundParallax', []))
    gsap_trigger_count = len(interactions.get('gsapScrollTrigger', {}).get('triggers', []))
    parallax_layers_count = len(interactions.get('parallax', {}).get('layers', []))

    log(f"\n{'='*60}")
    log(f"Design extraction complete!")
    log(f"")
    log(f"--- Design Tokens ---")
    log(f"Colors: {token_count}")
    log(f"Typography styles: {font_count}")
    log(f"")
    log(f"--- Animations ---")
    log(f"CSS Animations: {anim_count}")
    log(f"CSS Transitions: {trans_count}")
    log(f"@keyframes: {kf_count}")
    log(f"Web Animations (runtime): {web_anim_count}")
    log(f"Scroll before/after diffs: {scroll_ba_count}")
    log(f"Scroll CDP animations: {scroll_cdp_count}")
    log(f"Scroll runtime animations: {scroll_rt_count}")
    log(f"Hover diffs captured: {hover_diff_count}")
    log(f"")
    log(f"--- Interactions (NEW) ---")
    log(f"Scroll hijacked: {'YES' if scroll_hijacked else 'no'}")
    log(f"Scroll snap: {'YES' if scroll_snap_detected else 'no'}")
    log(f"Smooth scroll: {smooth_scroll_lib or 'none'}")
    log(f"Pinned sections: {pinned_count}")
    log(f"Parallax attrs: {parallax_attr_count}")
    log(f"CSS scroll-timeline: {css_scroll_timeline_count}")
    log(f"Custom cursor: {'YES' if cursor_follower else 'no'}")
    log(f"Tilt cards: {tilt_count}")
    log(f"Mouse-reactive elements: {mouse_dynamic_count}")
    log(f"Background parallax: {bg_parallax_count}")
    log(f"GSAP ScrollTrigger instances: {gsap_trigger_count}")
    log(f"Parallax layers (by ratio): {parallax_layers_count}")
    log(f"")
    log(f"--- Assets ---")
    log(f"Embedded videos: {video_count}")
    log(f"Sections: {section_count}")
    log(f"JS Libraries: {', '.join(libs_detected) if libs_detected else 'none detected'}")
    log(f"Screenshots: {len(section_screenshots)} sections + {len(full_screenshots)} full-page")
    log(f"Video: {'yes' if video_path else 'no'}")
    log(f"Data saved: {data_path}")
    log(f"{'='*60}")

    summary = {
        "status": "success",
        "url": url,
        "output_dir": output_dir,
        "design_data_file": data_path,
        "colors": token_count,
        "typography_styles": font_count,
        "css_animations": anim_count,
        "css_transitions": trans_count,
        "keyframes": kf_count,
        "web_animations_runtime": web_anim_count,
        "scroll_before_after_diffs": scroll_ba_count,
        "scroll_cdp_animations": scroll_cdp_count,
        "scroll_runtime_animations": scroll_rt_count,
        "hover_diffs": hover_diff_count,
        "embedded_videos": video_count,
        "sections": section_count,
        "js_libraries": libs_detected,
        "screenshots_sections": len(section_screenshots),
        "screenshots_fullpage": len(full_screenshots),
        "video": video_path,
        "scroll_hijacked": scroll_hijacked,
        "scroll_snap": scroll_snap_detected,
        "smooth_scroll": smooth_scroll_lib,
        "pinned_sections": pinned_count,
        "parallax_attrs": parallax_attr_count,
        "cursor_follower": cursor_follower,
        "tilt_cards": tilt_count,
        "mouse_reactive_elements": mouse_dynamic_count,
        "gsap_triggers": gsap_trigger_count,
        "parallax_layers": parallax_layers_count,
    }

    return summary


async def main():
    parser = argparse.ArgumentParser(description="Design system & animation scraper")
    parser.add_argument("--url", required=True, help="URL to extract design from")
    parser.add_argument("--output", required=True, help="Output directory path")
    parser.add_argument("--video", action="store_true", help="Record scroll video")
    parser.add_argument("--responsive", action="store_true", help="Capture at 3 viewports (desktop/tablet/mobile)")
    args = parser.parse_args()

    summary = await scrape_design(args.url, args.output, args.video, args.responsive)
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
