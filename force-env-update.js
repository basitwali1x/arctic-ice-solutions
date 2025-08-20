const fs = require('fs');
const path = require('path');

const distPath = path.join(__dirname, 'frontend/dist');
const env = {
  VITE_API_URL: process.env.VITE_API_URL || 'https://app-gkwjwdji.fly.dev',
  VITE_GOOGLE_MAPS_API_KEY: process.env.VITE_GOOGLE_MAPS_API_KEY || '',
  MODE: process.env.NODE_ENV || 'production'
};

console.log('🔧 Starting comprehensive environment update...');
console.log('Target directory:', distPath);
console.log('Environment variables:', { VITE_API_URL: env.VITE_API_URL });

if (!fs.existsSync(distPath)) {
  console.error('❌ Error: dist directory not found at', distPath);
  process.exit(1);
}

if (!env.VITE_API_URL.includes('app-gkwjwdji.fly.dev') && !env.VITE_API_URL.includes('api.yourchoiceice.com')) {
  console.error('❌ Error: Incorrect API URL detected:', env.VITE_API_URL);
  console.error('Expected URL should contain: app-gkwjwdji.fly.dev or api.yourchoiceice.com');
  process.exit(1);
}

const indexHtmlPath = path.join(distPath, 'index.html');
if (fs.existsSync(indexHtmlPath)) {
  let content = fs.readFileSync(indexHtmlPath, 'utf8');
  
  content = content.replace(
    /(const API_BASE_URL\s*=\s*["']).*?(["'])/g,
    `$1${env.VITE_API_URL}$2`
  );
  
  content = content.replace(
    /import\.meta\.env\.VITE_API_URL/g,
    `"${env.VITE_API_URL}"`
  );
  
  fs.writeFileSync(indexHtmlPath, content);
  console.log('✅ Updated index.html');
} else {
  console.log('⚠️  index.html not found');
}

const assetsPath = path.join(distPath, 'assets');
if (fs.existsSync(assetsPath)) {
  const jsFiles = fs.readdirSync(assetsPath).filter(file => file.endsWith('.js'));
  let updatedFiles = 0;
  
  jsFiles.forEach(file => {
    const filePath = path.join(assetsPath, file);
    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;
    
    const oldUrlPatterns = [
      /https:\/\/app-dfyyccxe\.fly\.dev/g,
      /https:\/\/app-eueptojk\.fly\.dev/g,
      /https:\/\/app-rawyclbe\.fly\.dev/g,
      /https:\/\/api\.yourchoiceice\.com/g,
      /http:\/\/localhost:8000/g
    ];
    
    const oldModePatterns = [
      /"development"/g,
      /'development'/g
    ];
    
    oldUrlPatterns.forEach(pattern => {
      if (pattern.test(content)) {
        content = content.replace(pattern, env.VITE_API_URL);
        modified = true;
      }
    });
    
    oldModePatterns.forEach(pattern => {
      if (pattern.test(content)) {
        content = content.replace(pattern, `"${env.MODE}"`);
        modified = true;
      }
    });
    
    if (content.includes('import.meta.env.VITE_API_URL')) {
      content = content.replace(
        /import\.meta\.env\.VITE_API_URL/g,
        `"${env.VITE_API_URL}"`
      );
      modified = true;
    }
    
    if (content.includes('API_BASE') || content.includes('apiUrl')) {
      content = content.replace(
        /(API_BASE|apiUrl)\s*[:=]\s*["'][^"']*["']/g,
        `$1:"${env.VITE_API_URL}"`
      );
      modified = true;
    }
    
    if (modified) {
      fs.writeFileSync(filePath, content);
      updatedFiles++;
      console.log(`✅ Updated ${file}`);
    }
  });
  
  console.log(`✅ Updated ${updatedFiles}/${jsFiles.length} JavaScript files in assets/`);
  
  const verificationFailed = jsFiles.some(file => {
    const filePath = path.join(assetsPath, file);
    const content = fs.readFileSync(filePath, 'utf8');
    return content.includes('localhost:8000') && !content.includes('app-gkwjwdji.fly.dev');
  });
  
  if (verificationFailed) {
    console.error('❌ Verification failed: Old URLs still present in assets');
    process.exit(1);
  } else {
    console.log('✅ Verification passed: No old URLs found in assets');
  }
} else {
  console.log('⚠️  assets directory not found');
}

const envConfigPath = path.join(distPath, 'env-config.js');
const envConfigContent = `window.env = ${JSON.stringify(env, null, 2)};
console.log('Environment configuration loaded:', window.env);`;

fs.writeFileSync(envConfigPath, envConfigContent);
console.log('✅ Created env-config.js');

const swPath = path.join(distPath, 'sw.js');
if (fs.existsSync(swPath)) {
  let content = fs.readFileSync(swPath, 'utf8');
  content = content.replace(
    /(const API_URL\s*=\s*["']).*?(["'])/g,
    `$1${env.VITE_API_URL}$2`
  );
  fs.writeFileSync(swPath, content);
  console.log('✅ Updated service worker');
}

const runtimeConfigPath = path.join(distPath, 'runtime-config.js');
const runtimeConfigContent = `
(function() {
  console.log('🔧 Runtime config override loading...');
  
  window.env = window.env || {};
  window.env.VITE_API_URL = "${env.VITE_API_URL}";
  
  const originalFetch = window.fetch;
  window.fetch = function(url, options) {
    if (typeof url === 'string') {
      if (url.includes('localhost:8000') && !url.includes('app-gkwjwdji.fly.dev')) {
        url = url.replace(/http:\\/\\/localhost:8000/, "${env.VITE_API_URL}");
        console.log('🔄 Redirected API call to:', url);
      }
    }
    return originalFetch.call(this, url, options);
  };
  
  console.log('✅ Runtime config override active - API URL:', window.env.VITE_API_URL);
})();
`;

fs.writeFileSync(runtimeConfigPath, runtimeConfigContent);
console.log('✅ Created runtime-config.js');

const indexFinalPath = path.join(distPath, 'index.html');
if (fs.existsSync(indexFinalPath)) {
  let content = fs.readFileSync(indexFinalPath, 'utf8');
  
  if (!content.includes('runtime-config.js')) {
    content = content.replace(
      '</head>',
      '  <script src="/runtime-config.js"></script>\n</head>'
    );
    fs.writeFileSync(indexFinalPath, content);
    console.log('✅ Injected runtime config into index.html');
  }
}

console.log('🎉 Comprehensive environment update completed successfully!');
console.log('Backend URL set to:', env.VITE_API_URL);
console.log('Runtime override active for any missed references');

console.log('\n📊 Update Summary:');
console.log('- Environment config file created');
console.log('- JavaScript assets updated');
console.log('- Runtime override script created');
console.log('- Index.html updated with runtime config');
console.log('- All old URLs replaced with:', env.VITE_API_URL);
