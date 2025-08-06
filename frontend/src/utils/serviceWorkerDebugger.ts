export const ServiceWorkerDebugger = {
  logCache: async () => {
    if (!('caches' in window)) {
      console.warn('Cache API not supported');
      return;
    }

    const keys = await caches.keys();
    console.group('🗄️ Service Worker Caches');
    
    await Promise.all(keys.map(async (key) => {
      const cache = await caches.open(key);
      const requests = await cache.keys();
      console.log(`%c${key}`, 'color: #4CAF50; font-weight: bold', {
        size: requests.length,
        urls: requests.map(r => r.url).slice(0, 5),
        totalUrls: requests.length
      });
    }));
    
    console.groupEnd();
  },

  clearAllCaches: async () => {
    if (!('caches' in window)) return;
    
    const keys = await caches.keys();
    await Promise.all(keys.map(key => caches.delete(key)));
    console.log('🧹 All caches cleared');
  },

  forceUpdate: () => {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
      console.log('🔄 Service worker update forced');
    }
  },

  simulateOffline: async () => {
    await ServiceWorkerDebugger.clearAllCaches();
    
    window.dispatchEvent(new Event('offline'));
    console.log('📴 Offline mode simulated');
    
    setTimeout(() => {
      window.dispatchEvent(new Event('online'));
      console.log('📶 Online mode restored');
    }, 5000);
  },

  getCacheStats: async () => {
    if (!('caches' in window)) return null;

    const keys = await caches.keys();
    let totalSize = 0;
    let totalEntries = 0;

    for (const key of keys) {
      const cache = await caches.open(key);
      const requests = await cache.keys();
      totalEntries += requests.length;
      
      for (const request of requests.slice(0, 10)) {
        try {
          const response = await cache.match(request);
          if (response) {
            const blob = await response.blob();
            totalSize += blob.size;
          }
        } catch (e) {
        }
      }
    }

    return {
      caches: keys.length,
      entries: totalEntries,
      estimatedSize: `${(totalSize / 1024 / 1024).toFixed(2)} MB`
    };
  }
};

if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
  (window as any).swDebugger = ServiceWorkerDebugger;
}

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    console.log('🔄 Service worker controller changed - reloading page');
    window.location.reload();
  });

  navigator.serviceWorker.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'CACHE_UPDATED') {
      console.log('📦 Cache updated:', event.data.url);
    }
  });
}
