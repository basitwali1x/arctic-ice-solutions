#!/bin/bash

set -e

echo "🔐 Generating SSL certificates for Arctic Ice Solutions demo environment..."

mkdir -p certs/demo

openssl genrsa -out certs/demo/demo.key 4096

openssl req -new -key certs/demo/demo.key -out certs/demo/demo.csr -subj "/C=US/ST=Alaska/L=Anchorage/O=Arctic Ice Solutions/OU=Engineering/CN=dashboard-flicker-app-myij7m4u.devinapps.com/emailAddress=engineering@arcticeice.com"

openssl x509 -req -days 365 -in certs/demo/demo.csr -signkey certs/demo/demo.key -out certs/demo/demo.crt

cat > certs/demo/demo.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = Alaska
L = Anchorage
O = Arctic Ice Solutions
OU = Engineering Department
CN = dashboard-flicker-app-myij7m4u.devinapps.com

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = dashboard-flicker-app-myij7m4u.devinapps.com
DNS.2 = localhost
DNS.3 = 127.0.0.1
DNS.4 = *.devinapps.com
EOF

openssl req -new -x509 -key certs/demo/demo.key -out certs/demo/demo-san.crt -days 365 -config certs/demo/demo.conf -extensions v3_req

echo "✅ SSL Certificates Generated Successfully!"
echo ""
echo "📁 Certificate Files:"
echo "   • certs/demo/demo.key (Private Key)"
echo "   • certs/demo/demo.crt (Certificate)"
echo "   • certs/demo/demo-san.crt (Certificate with SAN)"
echo "   • certs/demo/demo.csr (Certificate Signing Request)"
echo ""

echo "🔍 Certificate Information:"
openssl x509 -in certs/demo/demo-san.crt -text -noout | grep -A 5 "Subject:"
echo ""

cat > certs/demo/vite-https-config.js << EOF
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
EOF

echo "⚙️  Vite HTTPS configuration created: certs/demo/vite-https-config.js"
echo ""

cat > certs/demo/docker-https.yml << EOF
version: '3.8'
services:
  frontend:
    build: 
      context: ../../frontend
      dockerfile: Dockerfile
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./demo.key:/app/certs/demo.key:ro
      - ./demo-san.crt:/app/certs/demo.crt:ro
    environment:
      - HTTPS=true
      - SSL_CRT_FILE=/app/certs/demo.crt
      - SSL_KEY_FILE=/app/certs/demo.key
      - VITE_API_URL=https://app-gtgfifoe.fly.dev
    command: >
      sh -c "
        npm run build &&
        npx serve -s dist -l 443 --ssl-cert /app/certs/demo.crt --ssl-key /app/certs/demo.key
      "
EOF

echo "🐳 Docker HTTPS configuration created: certs/demo/docker-https.yml"
echo ""

cat > certs/demo/validate-certs.sh << EOF
#!/bin/bash

echo "🔍 Validating SSL certificates..."

if openssl x509 -in certs/demo/demo-san.crt -noout -checkend 86400; then
    echo "✅ Certificate is valid and not expiring within 24 hours"
else
    echo "⚠️  Certificate is expiring soon or invalid"
fi

cert_hash=\$(openssl x509 -noout -modulus -in certs/demo/demo-san.crt | openssl md5)
key_hash=\$(openssl rsa -noout -modulus -in certs/demo/demo.key | openssl md5)

if [ "\$cert_hash" = "\$key_hash" ]; then
    echo "✅ Certificate and private key match"
else
    echo "❌ Certificate and private key do not match"
fi

echo "📅 Certificate expires on:"
openssl x509 -in certs/demo/demo-san.crt -noout -enddate

echo ""
echo "🌐 Testing HTTPS connection..."
if curl -k -s -o /dev/null -w "%{http_code}" https://localhost:5174/ | grep -q "200"; then
    echo "✅ HTTPS connection successful"
else
    echo "⚠️  HTTPS connection failed (server may not be running)"
fi
EOF

chmod +x certs/demo/validate-certs.sh

echo "✅ Certificate validation script created: certs/demo/validate-certs.sh"
echo ""

cat > certs/demo/README.md << EOF

This directory contains SSL certificates for the Arctic Ice Solutions demo environment.


- \`demo.key\` - Private key (4096-bit RSA)
- \`demo.crt\` - Basic SSL certificate
- \`demo-san.crt\` - SSL certificate with Subject Alternative Names
- \`demo.csr\` - Certificate signing request
- \`vite-https-config.js\` - Vite HTTPS configuration
- \`docker-https.yml\` - Docker Compose HTTPS setup
- \`validate-certs.sh\` - Certificate validation script



1. Import the HTTPS configuration:
   \`\`\`javascript
   import { httpsConfig } from './certs/demo/vite-https-config.js';
   \`\`\`

2. Add to your \`vite.config.ts\`:
   \`\`\`typescript
   export default defineConfig({
     server: {
       ...httpsConfig,
       port: 5174
     }
   });
   \`\`\`

3. Start the dev server:
   \`\`\`bash
   npm run dev
   \`\`\`

4. Access via: \`https://localhost:5174\`


\`\`\`bash
cd certs/demo
docker-compose -f docker-https.yml up
\`\`\`


\`\`\`bash
./certs/demo/validate-certs.sh
\`\`\`


⚠️ **These are self-signed certificates for demo purposes only!**

- Do not use in production
- Browsers will show security warnings
- Add security exception to proceed
- Certificates are valid for 365 days


To regenerate certificates:

\`\`\`bash
./scripts/generate-demo-certs.sh
\`\`\`



1. Click "Advanced" in browser warning
2. Click "Proceed to localhost (unsafe)"
3. Or add certificate to browser's trusted certificates


Run validation script to check certificate integrity:

\`\`\`bash
./certs/demo/validate-certs.sh
\`\`\`

---

Generated on: $(date)
Valid until: $(openssl x509 -in certs/demo/demo-san.crt -noout -enddate | cut -d= -f2)
EOF

echo "📖 Installation instructions created: certs/demo/README.md"
echo ""
echo "🎉 Demo SSL certificate setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Run: chmod +x scripts/generate-demo-certs.sh"
echo "   2. Test: ./certs/demo/validate-certs.sh"
echo "   3. Configure Vite with HTTPS using the generated config"
echo "   4. Access demo at: https://localhost:5174"
echo ""
echo "⚠️  Remember: These are self-signed certificates for demo use only!"
