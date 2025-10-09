# API

## Endpoints

### GET /v1/ping

Returns a simple JSON object to confirm the service is running.

#### Example

```bash
curl -X GET http://localhost:3000/v1/ping
```

Expected response:

```json
{
  "ok": true
}
```
