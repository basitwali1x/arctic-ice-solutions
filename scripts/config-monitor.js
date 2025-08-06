(function() {
  const EXPECTED_URL = "https://app-rawyclbe.fly.dev";
  const CHECK_INTERVAL = 300000; // 5 minutes
  
  function checkConfiguration() {
    console.log('[Config Monitor] Checking API configuration...');
    
    if (window.env && window.env.VITE_API_URL !== EXPECTED_URL) {
      console.error(`[Config Monitor] CRITICAL: API URL mismatch! Expected ${EXPECTED_URL}, got ${window.env.VITE_API_URL}`);
      
      fetch('/api/alerts/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          error: `Config mismatch! Expected ${EXPECTED_URL}, got ${window.env?.VITE_API_URL}`,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent
        })
      }).catch(err => console.error('[Config Monitor] Failed to send alert:', err));
      
      return false;
    }
    
    fetch(`${EXPECTED_URL}/api/health`)
      .then(response => {
        if (response.ok) {
          console.log('[Config Monitor] ✅ Backend connectivity verified');
        } else {
          console.error('[Config Monitor] ❌ Backend health check failed:', response.status);
        }
      })
      .catch(error => {
        console.error('[Config Monitor] ❌ Backend connection failed:', error);
        
        const currentOrigin = window.location.origin;
        if (currentOrigin.includes('devinapps.com')) {
          console.log('[Config Monitor] Attempting to reload with cache bypass...');
          window.location.reload(true);
        }
      });
    
    return true;
  }
  
  checkConfiguration();
  
  setInterval(checkConfiguration, CHECK_INTERVAL);
  
  window.configMonitor = {
    check: checkConfiguration,
    expectedUrl: EXPECTED_URL
  };
  
  console.log('[Config Monitor] Initialized - checking every 5 minutes');
})();
