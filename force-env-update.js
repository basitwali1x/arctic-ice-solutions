const fs = require('fs');
const path = require('path');

const distPath = path.join(__dirname, 'frontend/dist');
const env = {
  VITE_API_URL: process.env.VITE_API_URL || 'https://app-rawyclbe.fly.dev',
  VITE_GOOGLE_MAPS_API_KEY: process.env.VITE_GOOGLE_MAPS_API_KEY || ''
};

console.log('Starting environment update...');
console.log('Target directory:', distPath);
console.log('Environment variables:', { VITE_API_URL: env.VITE_API_URL });

if (!fs.existsSync(distPath)) {
  console.error('Error: dist directory not found at', distPath);
  process.exit(1);
}

const indexPath = path.join(distPath, 'index.html');
if (fs.existsSync(indexPath)) {
  let content = fs.readFileSync(indexPath, 'utf8');
  
  content = content.replace(
    /(const API_BASE_URL\s*=\s*["']).*?(["'])/g,
    `$1${env.VITE_API_URL}$2`
  );
  
  content = content.replace(
    /import\.meta\.env\.VITE_API_URL/g,
    `"${env.VITE_API_URL}"`
  );
  
  fs.writeFileSync(indexPath, content);
  console.log('✅ Updated index.html');
} else {
  console.log('⚠️  index.html not found');
}

const assetsPath = path.join(distPath, 'assets');
if (fs.existsSync(assetsPath)) {
  const jsFiles = fs.readdirSync(assetsPath).filter(file => file.endsWith('.js'));
  
  jsFiles.forEach(file => {
    const filePath = path.join(assetsPath, file);
    let content = fs.readFileSync(filePath, 'utf8');
    
    content = content.replace(
      /https:\/\/app-[a-z0-9]+\.fly\.dev/g,
      env.VITE_API_URL
    );
    
    content = content.replace(
      /import\.meta\.env\.VITE_API_URL/g,
      `"${env.VITE_API_URL}"`
    );
    
    fs.writeFileSync(filePath, content);
  });
  
  console.log(`✅ Updated ${jsFiles.length} JavaScript files in assets/`);
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

console.log('🎉 Environment update completed successfully!');
console.log('Backend URL set to:', env.VITE_API_URL);
