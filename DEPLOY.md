# PalmReadingWeb Docker Deploy

This project uses an external Nginx on the host.

- Backend: Docker container, FastAPI on `127.0.0.1:8000`
- Frontend: static Vite build copied to host Nginx web root
- Public path: `/plamReading/`
- API path: `/api/`

## 1. Backend env

Create or update `backend/.env` on the server:

```env
PALM_AI_PROVIDER=mock
PALM_AI_ANALYSIS_ENABLED=true
PALM_CORS_ORIGINS=["https://www.zmintz.com","https://zmintz.com"]
```

For a real model provider:

```env
PALM_AI_PROVIDER=openai_compatible
PALM_AI_API_KEY=your_api_key
PALM_AI_BASE_URL=https://api.openai.com/v1
PALM_AI_MODEL=gpt-4o-mini
PALM_AI_ANALYSIS_ENABLED=true
PALM_CORS_ORIGINS=["https://www.zmintz.com","https://zmintz.com"]
```

## 2. Build and run backend

```bash
docker compose up -d --build
docker compose ps
```

Backend health check:

```bash
curl http://127.0.0.1:8000/api/health
```

## 3. Build frontend for `/plamReading/`

```bash
cd frontend
npm ci
VITE_BASE_PATH=/plamReading/ npm run build
```

Copy the build output to the external Nginx static directory:

```bash
rm -rf /usr/share/nginx/html/plamReading
mkdir -p /usr/share/nginx/html/plamReading
cp -r dist/* /usr/share/nginx/html/plamReading/
```

## 4. External Nginx locations

Add these locations to the existing `server { listen 443 ssl; ... }` block.

```nginx
root /usr/share/nginx/html;
index index.html;

location ^~ /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    client_max_body_size 10m;

    proxy_connect_timeout 60s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;
}

location = /plamReading {
    return 301 /plamReading/;
}

location ^~ /plamReading/assets/ {
    try_files $uri =404;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location ^~ /plamReading/ {
    try_files $uri $uri/ /plamReading/index.html;
}
```

Then reload Nginx:

```bash
nginx -t
systemctl reload nginx
```

## 5. Public URLs

- Home: `https://www.zmintz.com/plamReading/`
- Result page: `https://www.zmintz.com/plamReading/reading/{readingId}?token={shareToken}`
- Share page: `https://www.zmintz.com/plamReading/r/{shareToken}`
- API: `https://www.zmintz.com/api/v1/palm-readings`

## 6. Common operations

View backend logs:

```bash
docker compose logs -f palm-reading-api
```

Restart backend:

```bash
docker compose restart palm-reading-api
```

Stop backend:

```bash
docker compose down
```

Keep uploaded images and generated reports:

```bash
docker volume ls | grep palm-reading-data
```
