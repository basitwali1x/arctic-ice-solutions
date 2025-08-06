// Add this to your vite.config.ts for HTTPS development
import fs from 'fs';

export const httpsConfig = {
  https: {
    key: fs.readFileSync('certs/demo/demo.key'),
    cert: fs.readFileSync('certs/demo/demo-san.crt')
  }
};

// Usage in vite.config.ts:
// import { httpsConfig } from './certs/demo/vite-https-config.js';
// 
// export default defineConfig({
//   server: {
//     ...httpsConfig,
//     port: 5174
//   }
// });
