const http = require('http');
const https = require('https');
const url = require('url');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Load credentials from ~/.copilot/youtube-tokens/credentials.json
const CREDS_PATH = path.join(process.env.USERPROFILE, '.copilot', 'youtube-tokens', 'credentials.json');
if (!fs.existsSync(CREDS_PATH)) {
  console.error('ERROR: No credentials file found at ' + CREDS_PATH);
  console.error('Create credentials.json with { "client_id": "...", "client_secret": "..." }');
  console.error('Get these values from your team lead or Google Cloud Console.');
  process.exit(1);
}
const creds = JSON.parse(fs.readFileSync(CREDS_PATH, 'utf8'));
const CLIENT_ID = creds.client_id;
const CLIENT_SECRET = creds.client_secret;
const REDIRECT_PORT = 3847;
const REDIRECT_URI = `http://localhost:${REDIRECT_PORT}`;
const SCOPES = [
  'https://www.googleapis.com/auth/youtube',
  'https://www.googleapis.com/auth/youtube.force-ssl',
  'https://www.googleapis.com/auth/youtube.upload',
  'https://www.googleapis.com/auth/yt-analytics.readonly'
];
const CHANNEL_NAME = process.argv[2];
if (!CHANNEL_NAME) {
  console.error('Usage: node oauth-flow.js <channel-name>');
  console.error('Example: node oauth-flow.js reactor');
  process.exit(1);
}
const TOKENS_DIR = path.join(process.env.USERPROFILE, '.copilot', 'youtube-tokens');
if (!fs.existsSync(TOKENS_DIR)) fs.mkdirSync(TOKENS_DIR, { recursive: true });
const TOKEN_PATH = path.join(TOKENS_DIR, `${CHANNEL_NAME}.json`);

const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
  `client_id=${encodeURIComponent(CLIENT_ID)}` +
  `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}` +
  `&response_type=code` +
  `&scope=${encodeURIComponent(SCOPES.join(' '))}` +
  `&access_type=offline` +
  `&prompt=consent`;

console.log('Starting OAuth flow...');
console.log('Opening browser for authorization...\n');

// Start local server to catch the redirect
const server = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);
  const code = parsed.query.code;
  const error = parsed.query.error;

  if (error) {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`<h1>Authorization denied</h1><p>${error}</p><p>You can close this tab.</p>`);
    console.error('Authorization denied:', error);
    server.close();
    process.exit(1);
  }

  if (code) {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end('<h1>✅ Authorization successful!</h1><p>You can close this tab and return to the terminal.</p>');

    console.log('Got authorization code. Exchanging for tokens...');

    try {
      const tokens = await exchangeCode(code);
      // Save tokens
      const tokenData = {
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        token_type: tokens.token_type,
        expiry_date: Date.now() + (tokens.expires_in * 1000),
        scope: tokens.scope
      };
      fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokenData, null, 2));
      console.log(`\n✅ Tokens saved to: ${TOKEN_PATH}`);
      console.log(`   Access token expires in: ${tokens.expires_in} seconds`);
      console.log(`   Refresh token: ${tokens.refresh_token ? 'received' : 'NOT received'}`);
    } catch (err) {
      console.error('Token exchange failed:', err.message);
    }

    server.close();
  }
});

server.listen(REDIRECT_PORT, () => {
  console.log(`Listening on port ${REDIRECT_PORT} for OAuth callback...\n`);
  // Open browser
  exec(`start "" "${authUrl}"`);
});

function exchangeCode(code) {
  return new Promise((resolve, reject) => {
    const postData = new URLSearchParams({
      code,
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      redirect_uri: REDIRECT_URI,
      grant_type: 'authorization_code'
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
        if (parsed.error) reject(new Error(`${parsed.error}: ${parsed.error_description}`));
        else resolve(parsed);
      });
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}
