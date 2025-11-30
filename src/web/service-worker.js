// Service Worker for AgentDaf1.1 Dashboard PWA
const CACHE_NAME = 'agentdaf-v1.0.0';
const STATIC_CACHE = 'agentdaf-static-v1.0.0';
const DATA_CACHE = 'agentdaf-data-v1.0.0';

// Files to cache for offline functionality
const STATIC_ASSETS = [
  '/',
  '/src/web/templates/enhanced-dashboard.html',
  '/src/web/styles/variables.css',
  '/src/web/styles/dashboard.css',
  '/src/web/styles/themes.css',
  '/src/web/styles/mobile.css',
  '/src/web/components/theme-manager.js',
  '/src/web/components/data-loader.js',
  '/src/web/components/scoreboard.js',
  '/src/web/components/charts.js',
  '/src/web/scripts/main.js',
  '/src/web/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js'
];

// Data files that should be cached
const DATA_FILES = [
  '/data/monday_data.json',
  '/data/scoreboard-data.json'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('Service Worker: Static assets cached');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Failed to cache static assets:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DATA_CACHE) {
              console.log('Service Worker: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle different types of requests
  if (isDataRequest(url)) {
    event.respondWith(handleDataRequest(request));
  } else if (isStaticRequest(url)) {
    event.respondWith(handleStaticRequest(request));
  } else {
    event.respondWith(handleNavigationRequest(request));
  }
});

// Handle data requests with network-first strategy
async function handleDataRequest(request) {
  try {
    // Try network first for fresh data
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache fresh data
      const cache = await caches.open(DATA_CACHE);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
  } catch (error) {
    console.log('Service Worker: Network failed for data, trying cache');
  }
  
  // Fallback to cache
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Return offline fallback
  return new Response(
    JSON.stringify({
      error: true,
      message: 'Offline - Keine Daten verfügbar',
      positive: [],
      negative: [],
      combined: [],
      metadata: {
        totalPlayers: 0,
        totalAlliances: 0,
        lastUpdate: new Date().toISOString(),
        offline: true
      }
    }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    }
  );
}

// Handle static asset requests with cache-first strategy
async function handleStaticRequest(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    // Update cache in background
    updateCacheInBackground(request);
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
  } catch (error) {
    console.log('Service Worker: Network failed for static asset');
  }
  
  // Return 404 for missing static assets
  return new Response('Resource not found', { status: 404 });
}

// Handle navigation requests
async function handleNavigationRequest(request) {
  try {
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed for navigation, serving offline page');
    
    // Serve cached main page
    const cachedResponse = await caches.match('/');
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Basic offline fallback
    return new Response(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>AgentDaf1.1 - Offline</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          body { font-family: system-ui, sans-serif; text-align: center; padding: 2rem; background: #1E1E2F; color: white; }
          .offline-icon { font-size: 4rem; margin-bottom: 1rem; }
          h1 { color: #00FF88; }
          .retry-btn { background: #00FF88; color: #1E1E2F; border: none; padding: 1rem 2rem; border-radius: 8px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
        </style>
      </head>
      <body>
        <div class="offline-icon">🏆</div>
        <h1>AgentDaf1.1 Dashboard</h1>
        <p>Sie sind offline. Einige Funktionen sind möglicherweise nicht verfügbar.</p>
        <button class="retry-btn" onclick="location.reload()">Erneut versuchen</button>
      </body>
      </html>
    `, {
      status: 200,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}

// Update cache in background
async function updateCacheInBackground(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse);
    }
  } catch (error) {
    // Silent fail for background updates
  }
}

// Helper functions
function isDataRequest(url) {
  return url.pathname.includes('/data/') || url.pathname.endsWith('.json');
}

function isStaticRequest(url) {
  return url.pathname.includes('/src/web/') || 
         url.pathname.includes('/components/') || 
         url.pathname.includes('/scripts/') ||
         url.pathname.includes('/styles/') ||
         url.hostname === 'cdn.jsdelivr.net' ||
         url.hostname === 'cdnjs.cloudflare.com' ||
         url.hostname === 'fonts.googleapis.com';
}

// Background sync for data updates
self.addEventListener('sync', (event) => {
  if (event.tag === 'data-sync') {
    event.waitUntil(syncData());
  }
});

async function syncData() {
  try {
    // Refresh all cached data files
    const cache = await caches.open(DATA_CACHE);
    const requests = await cache.keys();
    
    await Promise.all(
      requests.map(async (request) => {
        try {
          const response = await fetch(request);
          if (response.ok) {
            await cache.put(request, response);
          }
        } catch (error) {
          console.log('Failed to sync:', request.url);
        }
      })
    );
    
    console.log('Service Worker: Data sync completed');
  } catch (error) {
    console.error('Service Worker: Data sync failed:', error);
  }
}

// Push notification handling
self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  const options = {
    body: event.data.text(),
    icon: '/data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><text y=\'.9em\' font-size=\'90\'>🏆</text></svg>',
    badge: '/data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><text y=\'.9em\' font-size=\'90\'>🏆</text></svg>',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Dashboard öffnen',
        icon: '/data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><text y=\'.9em\' font-size=\'90\'>👁️</text></svg>'
      },
      {
        action: 'close',
        title: 'Schließen',
        icon: '/data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><text y=\'.9em\' font-size=\'90\'>❌</text></svg>'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('AgentDaf1.1 Dashboard', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Periodic background sync
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'data-update') {
    event.waitUntil(syncData());
  }
});

console.log('Service Worker: Loaded');