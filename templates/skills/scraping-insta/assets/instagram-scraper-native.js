'use strict';

/**
 * Native Instagram Scraper
 *
 * Scrapes public Instagram profiles and posts using Instagram's
 * internal REST API (no Apify, no login, $0 cost).
 *
 * Endpoints used:
 *   - /api/v1/users/web_profile_info/ — profile metadata + first 12 posts
 *   - /api/v1/feed/user/{id}/ — paginated posts (12 per page)
 *
 * Rate limit: ~200 req/hour from a single IP. We add delays between pages.
 *
 * @module monitor-server/instagram-scraper-native
 */

// ─── Configuration ──────────────────────────────────────────────

const IG_BASE = 'https://www.instagram.com';
const IG_APP_ID = '936619743392459';
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';
const POSTS_PER_PAGE = 12;
const DELAY_BETWEEN_PAGES_MS = 2000;

const HEADERS = {
  'User-Agent': USER_AGENT,
  'X-IG-App-ID': IG_APP_ID,
  'Accept': '*/*',
  'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
};

// ─── Profile Fetcher ────────────────────────────────────────────

/**
 * Fetch profile metadata and first page of posts.
 *
 * @param {string} username - Instagram username (without @)
 * @returns {Promise<{profile: object, posts: object[], userId: string, cursor: string|null}>}
 */
async function fetchProfile(username) {
  const url = `${IG_BASE}/api/v1/users/web_profile_info/?username=${encodeURIComponent(username)}`;

  const response = await fetch(url, { headers: HEADERS });

  if (response.status === 404) {
    throw new Error(`Profile @${username} not found (404)`);
  }
  if (!response.ok) {
    throw new Error(`Instagram API returned ${response.status} for @${username}`);
  }

  const data = await response.json();
  const user = data?.data?.user;

  if (!user) {
    throw new Error(`No user data returned for @${username}`);
  }

  if (user.is_private) {
    throw new Error(`Profile @${username} is private — cannot scrape`);
  }

  // Extract profile metadata
  const profile = {
    fullName: user.full_name || username,
    biography: user.biography || '',
    followersCount: user.edge_followed_by?.count || 0,
    followsCount: user.edge_follow?.count || 0,
    postsCount: user.edge_owner_to_timeline_media?.count || 0,
    profilePicUrl: user.profile_pic_url_hd || user.profile_pic_url || '',
    isVerified: user.is_verified || false,
    userId: user.id,
    externalUrl: user.external_url || '',
    category: user.category_name || '',
  };

  // Extract first page of posts from GraphQL response
  const media = user.edge_owner_to_timeline_media || {};
  const edges = media.edges || [];
  const posts = edges.map((edge) => normalizeGraphQLPost(edge.node, username, profile.fullName));

  const pageInfo = media.page_info || {};
  const cursor = pageInfo.has_next_page ? pageInfo.end_cursor : null;

  return { profile, posts, userId: user.id, cursor };
}

// ─── Posts Paginator ────────────────────────────────────────────

/**
 * Fetch additional pages of posts using the v1 feed API.
 *
 * @param {string} userId - Instagram user ID (numeric)
 * @param {string} username - For author attribution
 * @param {string} fullName - For author attribution
 * @param {object} [options]
 * @param {number} [options.maxPosts=60] - Maximum total posts to fetch
 * @param {number} [options.existingCount=0] - Posts already fetched
 * @returns {Promise<object[]>} - Array of normalized posts
 */
async function fetchMorePosts(userId, username, fullName, options = {}) {
  const { maxPosts = 60, existingCount = 0 } = options;
  const remaining = maxPosts - existingCount;

  if (remaining <= 0) return [];

  const allPosts = [];
  let maxId = '';
  let page = 0;

  while (allPosts.length < remaining) {
    page++;
    const url = `${IG_BASE}/api/v1/feed/user/${userId}/?count=${POSTS_PER_PAGE}${maxId ? `&max_id=${maxId}` : ''}`;

    try {
      const response = await fetch(url, { headers: HEADERS });

      if (!response.ok) {
        console.warn(`[IGScraper] Feed page ${page} returned ${response.status}, stopping pagination`);
        break;
      }

      const data = await response.json();
      const items = data.items || [];

      if (items.length === 0) break;

      for (const item of items) {
        allPosts.push(normalizeFeedPost(item, username, fullName));
        if (allPosts.length >= remaining) break;
      }

      if (!data.more_available || !data.next_max_id) break;

      maxId = data.next_max_id;

      // Rate limit delay between pages
      await new Promise((r) => setTimeout(r, DELAY_BETWEEN_PAGES_MS));
    } catch (err) {
      console.warn(`[IGScraper] Feed page ${page} failed: ${err.message}`);
      break;
    }
  }

  return allPosts;
}

// ─── Full Profile Scraper ───────────────────────────────────────

/**
 * Scrape a complete public Instagram profile.
 *
 * @param {string} username
 * @param {object} [options]
 * @param {number} [options.maxPosts=60]
 * @returns {Promise<{profile: object, posts: object[]}>}
 */
async function scrapeInstagramProfile(username, options = {}) {
  const { maxPosts = 60 } = options;

  console.log(`[IGScraper] Fetching profile @${username}...`);

  // Step 1: Get profile + first 12 posts
  const { profile, posts: firstPosts, userId } = await fetchProfile(username);

  console.log(`[IGScraper] Profile: ${profile.fullName} (${profile.followersCount} followers, ${profile.postsCount} posts)`);
  console.log(`[IGScraper] First page: ${firstPosts.length} posts`);

  if (firstPosts.length >= maxPosts) {
    return { profile, posts: firstPosts.slice(0, maxPosts) };
  }

  // Step 2: Paginate for more posts
  const morePosts = await fetchMorePosts(userId, username, profile.fullName, {
    maxPosts,
    existingCount: firstPosts.length,
  });

  console.log(`[IGScraper] Additional pages: ${morePosts.length} posts`);

  const allPosts = [...firstPosts, ...morePosts].slice(0, maxPosts);

  console.log(`[IGScraper] Total: ${allPosts.length} posts for @${username}`);

  return { profile, posts: allPosts };
}

// ─── Normalizers ────────────────────────────────────────────────

/**
 * Normalize a post from the GraphQL (web_profile_info) response.
 * Schema: edge.node with __typename, shortcode, edge_media_preview_like, etc.
 */
function normalizeGraphQLPost(node, username, fullName) {
  const caption = node.edge_media_to_caption?.edges?.[0]?.node?.text || '';

  let contentType = 'post';
  if (node.__typename === 'GraphVideo' || node.is_video) contentType = 'reel';
  else if (node.__typename === 'GraphSidecar') contentType = 'carousel';

  return {
    url: `https://www.instagram.com/p/${node.shortcode}/`,
    shortCode: node.shortcode,
    platform: 'instagram',
    content_type: contentType,
    title: caption.substring(0, 80),
    caption,
    engagement_metrics: {
      likes: node.edge_media_preview_like?.count || node.edge_liked_by?.count || 0,
      comments: node.edge_media_to_comment?.count || 0,
      views: node.video_view_count || 0,
    },
    author_username: username,
    author_name: fullName,
    published_at: node.taken_at_timestamp
      ? new Date(node.taken_at_timestamp * 1000).toISOString()
      : null,
    video_download_url: node.video_url || null,
    duration_seconds: null, // Not available in GraphQL response
    slide_count: node.edge_sidecar_to_children?.edges?.length || null,
    is_video: node.is_video || false,
    thumbnail_url: node.display_url || node.thumbnail_src || null,
  };
}

/**
 * Normalize a post from the v1 feed API response.
 * Schema: item with code, media_type, like_count, video_versions, etc.
 */
function normalizeFeedPost(item, username, fullName) {
  const caption = item.caption?.text || '';

  // media_type: 1=image, 2=video, 8=carousel
  let contentType = 'post';
  if (item.media_type === 2) contentType = 'reel';
  else if (item.media_type === 8) contentType = 'carousel';

  // Get video URL from video_versions
  const videoUrl = item.video_versions?.[0]?.url || null;

  return {
    url: `https://www.instagram.com/p/${item.code}/`,
    shortCode: item.code,
    platform: 'instagram',
    content_type: contentType,
    title: caption.substring(0, 80),
    caption,
    engagement_metrics: {
      likes: item.like_count || 0,
      comments: item.comment_count || 0,
      views: item.play_count || item.view_count || 0,
    },
    author_username: username,
    author_name: fullName,
    published_at: item.taken_at
      ? new Date(item.taken_at * 1000).toISOString()
      : null,
    video_download_url: videoUrl,
    duration_seconds: item.video_duration ? Math.round(item.video_duration) : null,
    slide_count: item.carousel_media_count || item.carousel_media?.length || null,
    is_video: item.media_type === 2,
    thumbnail_url: item.image_versions2?.candidates?.[0]?.url || null,
  };
}

// ─── Exports ────────────────────────────────────────────────────

module.exports = {
  scrapeInstagramProfile,
  fetchProfile,
  fetchMorePosts,
};
