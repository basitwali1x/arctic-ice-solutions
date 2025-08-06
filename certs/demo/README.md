
This directory contains SSL certificates for the Arctic Ice Solutions demo environment.


- `demo.key` - Private key (4096-bit RSA)
- `demo.crt` - Basic SSL certificate
- `demo-san.crt` - SSL certificate with Subject Alternative Names
- `demo.csr` - Certificate signing request
- `vite-https-config.js` - Vite HTTPS configuration
- `docker-https.yml` - Docker Compose HTTPS setup
- `validate-certs.sh` - Certificate validation script



1. Import the HTTPS configuration:
   ```javascript
   import { httpsConfig } from './certs/demo/vite-https-config.js';
   ```

2. Add to your `vite.config.ts`:
   ```typescript
   export default defineConfig({
     server: {
       ...httpsConfig,
       port: 5174
     }
   });
   ```

3. Start the dev server:
   ```bash
   npm run dev
   ```

4. Access via: `https://localhost:5174`


```bash
cd certs/demo
docker-compose -f docker-https.yml up
```


```bash
./certs/demo/validate-certs.sh
```


⚠️ **These are self-signed certificates for demo purposes only!**

- Do not use in production
- Browsers will show security warnings
- Add security exception to proceed
- Certificates are valid for 365 days


To regenerate certificates:

```bash
./scripts/generate-demo-certs.sh
```



1. Click "Advanced" in browser warning
2. Click "Proceed to localhost (unsafe)"
3. Or add certificate to browser's trusted certificates


Run validation script to check certificate integrity:

```bash
./certs/demo/validate-certs.sh
```

---

Generated on: Wed Aug  6 15:51:52 UTC 2025
Valid until: Aug  6 15:51:52 2026 GMT
