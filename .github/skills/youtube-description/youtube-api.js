/**
 * YouTube Data API v3 helper for the youtube-description skill.
 *
 * Usage:
 *   node youtube-api.js <channel> get    <videoId>
 *   node youtube-api.js <channel> update <videoId> <title> <descriptionFile>
 *   node youtube-api.js <channel> list   [maxResults]
 *
 * Tokens are read from ~/.copilot/youtube-tokens/<channel>.json
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const TOKENS_DIR = path.join(process.env.USERPROFILE, '.copilot', 'youtube-tokens');

// --- Token Management ---

function loadToken(channel) {
  const tokenPath = path.join(TOKENS_DIR, `${channel}.json`);
  if (!fs.existsSync(tokenPath)) {
    console.error(`ERROR: No token found for channel "${channel}".`);
    console.error(`Run: node ~/.copilot/youtube-tokens/auth.js ${channel}`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(tokenPath, 'utf8'));
}

function saveToken(channel, tokenData) {
  const tokenPath = path.join(TOKENS_DIR, `${channel}.json`);
  fs.writeFileSync(tokenPath, JSON.stringify(tokenData, null, 2));
}

function isTokenExpired(tokenData) {
  return Date.now() >= (tokenData.expiry_date - 60000); // 1 min buffer
}

function refreshAccessToken(tokenData) {
  return new Promise((resolve, reject) => {
    const postData = new URLSearchParams({
      client_id: tokenData.client_id,
      client_secret: tokenData.client_secret,
      refresh_token: tokenData.refresh_token,
      grant_type: 'refresh_token'
    }).toString();

    const options = {
      hostname: 'oauth2.googleapis.com',
      path: '/token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const parsed = JSON.parse(data);
        if (parsed.error) {
          reject(new Error(`Token refresh failed: ${parsed.error} — ${parsed.error_description}`));
        } else {
          resolve(parsed);
        }
      });
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

async function getValidToken(channel) {
  const tokenData = loadToken(channel);
  if (isTokenExpired(tokenData)) {
    const refreshed = await refreshAccessToken(tokenData);
    tokenData.access_token = refreshed.access_token;
    tokenData.expiry_date = Date.now() + (refreshed.expires_in * 1000);
    saveToken(channel, tokenData);
  }
  return tokenData.access_token;
}

// --- API Calls ---

function apiRequest(method, path, accessToken, body) {
  return new Promise((resolve, reject) => {
    const bodyStr = body ? JSON.stringify(body) : null;
    const options = {
      hostname: 'www.googleapis.com',
      path,
      method,
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/json',
        ...(bodyStr ? {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(bodyStr)
        } : {})
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const parsed = JSON.parse(data);
        if (res.statusCode >= 400) {
          reject(new Error(`API error ${res.statusCode}: ${JSON.stringify(parsed.error || parsed, null, 2)}`));
        } else {
          resolve(parsed);
        }
      });
    });
    req.on('error', reject);
    if (bodyStr) req.write(bodyStr);
    req.end();
  });
}

async function getVideo(channel, videoId) {
  const token = await getValidToken(channel);
  const result = await apiRequest(
    'GET',
    `/youtube/v3/videos?part=snippet,status&id=${videoId}`,
    token
  );
  if (!result.items || result.items.length === 0) {
    console.error(`ERROR: Video ${videoId} not found on channel "${channel}".`);
    process.exit(1);
  }
  const video = result.items[0];
  console.log(JSON.stringify({
    id: video.id,
    title: video.snippet.title,
    description: video.snippet.description,
    tags: video.snippet.tags || [],
    categoryId: video.snippet.categoryId,
    privacyStatus: video.status.privacyStatus,
    publishedAt: video.snippet.publishedAt
  }, null, 2));
}

async function updateVideo(channel, videoId, title, descriptionFile) {
  const token = await getValidToken(channel);
  const description = fs.readFileSync(descriptionFile, 'utf8');

  // First, get the current video to preserve existing fields
  const current = await apiRequest(
    'GET',
    `/youtube/v3/videos?part=snippet,status&id=${videoId}`,
    token
  );

  if (!current.items || current.items.length === 0) {
    console.error(`ERROR: Video ${videoId} not found.`);
    process.exit(1);
  }

  const snippet = current.items[0].snippet;

  // Update only title and description, preserve everything else
  const body = {
    id: videoId,
    snippet: {
      title: title,
      description: description,
      categoryId: snippet.categoryId,
      tags: snippet.tags || [],
      defaultLanguage: snippet.defaultLanguage,
      defaultAudioLanguage: snippet.defaultAudioLanguage
    }
  };

  const result = await apiRequest(
    'PUT',
    '/youtube/v3/videos?part=snippet',
    token,
    body
  );

  console.log(JSON.stringify({
    success: true,
    id: result.id,
    title: result.snippet.title,
    descriptionLength: result.snippet.description.length,
    updatedAt: new Date().toISOString()
  }, null, 2));
}

async function listVideos(channel, maxResults = 10) {
  const token = await getValidToken(channel);

  // Get the channel's uploads playlist
  const channelRes = await apiRequest(
    'GET',
    '/youtube/v3/channels?part=contentDetails&mine=true',
    token
  );

  const uploadsPlaylistId = channelRes.items[0].contentDetails.relatedPlaylists.uploads;

  const playlistRes = await apiRequest(
    'GET',
    `/youtube/v3/playlistItems?part=snippet&playlistId=${uploadsPlaylistId}&maxResults=${maxResults}`,
    token
  );

  const videos = playlistRes.items.map(item => ({
    videoId: item.snippet.resourceId.videoId,
    title: item.snippet.title,
    publishedAt: item.snippet.publishedAt
  }));

  console.log(JSON.stringify(videos, null, 2));
}

// --- Main ---

(async () => {
  const [,, channel, command, ...args] = process.argv;

  if (!channel || !command) {
    console.log('YouTube Data API v3 Helper');
    console.log('');
    console.log('Usage:');
    console.log('  node youtube-api.js <channel> get    <videoId>');
    console.log('  node youtube-api.js <channel> update <videoId> <title> <descriptionFile>');
    console.log('  node youtube-api.js <channel> list   [maxResults]');
    console.log('');
    console.log('Available channels:');
    const files = fs.readdirSync(TOKENS_DIR).filter(f => f.endsWith('.json'));
    files.forEach(f => console.log(`  - ${f.replace('.json', '')}`));
    process.exit(0);
  }

  switch (command) {
    case 'get':
      if (!args[0]) { console.error('Missing videoId'); process.exit(1); }
      await getVideo(channel, args[0]);
      break;
    case 'update':
      if (!args[0] || !args[1] || !args[2]) {
        console.error('Usage: update <videoId> <title> <descriptionFile>');
        process.exit(1);
      }
      await updateVideo(channel, args[0], args[1], args[2]);
      break;
    case 'list':
      await listVideos(channel, args[0] || 10);
      break;
    default:
      console.error(`Unknown command: ${command}`);
      process.exit(1);
  }
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
