#!/bin/bash
# veo-image-to-video.sh
# Submit an image + prompt to Veo 3.1 Fast and poll until ready.
# Usage: veo-image-to-video.sh <image_path> <prompt> [output_path]

set -euo pipefail

IMAGE_PATH="${1:-}"
PROMPT="${2:-}"
OUTPUT_PATH="${3:-./veo-out-$(date +%s).mp4}"

if [ -z "$IMAGE_PATH" ] || [ -z "$PROMPT" ]; then
  echo "Usage: $0 <image_path> <prompt> [output_path]" >&2
  exit 64
fi

if [ ! -f "$IMAGE_PATH" ]; then
  echo "ERROR: image not found at $IMAGE_PATH" >&2
  exit 66
fi

ENV_FILE="/root/teste-aios/aios-core/apps/monitor-server/.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: .env not found at $ENV_FILE" >&2
  exit 66
fi

GOOGLE_API_KEY="$(grep -E '^GOOGLE_API_KEY=' "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '\r')"
if [ -z "${GOOGLE_API_KEY:-}" ]; then
  echo "ERROR: GOOGLE_API_KEY missing in $ENV_FILE" >&2
  exit 78
fi

case "$IMAGE_PATH" in
  *.png|*.PNG) MIME="image/png" ;;
  *.jpg|*.jpeg|*.JPG|*.JPEG) MIME="image/jpeg" ;;
  *.webp|*.WEBP) MIME="image/webp" ;;
  *) MIME="image/png" ;;
esac

echo "[veo] encoding image ($MIME)..."
IMAGE_B64="$(base64 -w0 "$IMAGE_PATH")"

TMP_PAYLOAD="$(mktemp --suffix=.json)"
trap 'rm -f "$TMP_PAYLOAD"' EXIT

PROMPT_ESCAPED="$(printf '%s' "$PROMPT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"

cat > "$TMP_PAYLOAD" <<JSON
{
  "instances": [
    {
      "prompt": ${PROMPT_ESCAPED},
      "image": {
        "bytesBase64Encoded": "${IMAGE_B64}",
        "mimeType": "${MIME}"
      }
    }
  ],
  "parameters": {
    "aspectRatio": "16:9",
    "personGeneration": "allow_all",
    "durationSeconds": 8
  }
}
JSON

SUBMIT_URL="https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning?key=${GOOGLE_API_KEY}"

echo "[veo] submitting prediction..."
SUBMIT_RESP="$(curl -sS -X POST "$SUBMIT_URL" -H 'Content-Type: application/json' --data-binary @"$TMP_PAYLOAD" -w '\n__HTTP__:%{http_code}')"
HTTP_CODE="$(printf '%s' "$SUBMIT_RESP" | tail -1 | sed 's/__HTTP__://')"
SUBMIT_BODY="$(printf '%s' "$SUBMIT_RESP" | sed '$d')"

if [ "$HTTP_CODE" = "429" ]; then
  echo "ERROR: rate limited (429). Body: $SUBMIT_BODY" >&2
  exit 75
fi
if [ "$HTTP_CODE" != "200" ]; then
  echo "ERROR: submit failed http=$HTTP_CODE body=$SUBMIT_BODY" >&2
  exit 1
fi

OP_NAME="$(printf '%s' "$SUBMIT_BODY" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("name",""))')"
if [ -z "$OP_NAME" ]; then
  echo "ERROR: no operation name in response: $SUBMIT_BODY" >&2
  exit 1
fi
echo "[veo] operation: $OP_NAME"

POLL_URL="https://generativelanguage.googleapis.com/v1beta/${OP_NAME}?key=${GOOGLE_API_KEY}"
VIDEO_URI=""
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  sleep 15
  echo "[veo] poll attempt $i ..."
  POLL_BODY="$(curl -sS "$POLL_URL")"
  DONE="$(printf '%s' "$POLL_BODY" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(str(d.get("done", False)).lower())')"
  if [ "$DONE" = "true" ]; then
    VIDEO_URI="$(printf '%s' "$POLL_BODY" | python3 -c 'import json,sys; d=json.load(sys.stdin); r=d.get("response",{}).get("generateVideoResponse",{}).get("generatedSamples",[]); print(r[0].get("video",{}).get("uri","") if r else "")')"
    if [ -z "$VIDEO_URI" ]; then
      echo "ERROR: operation done but no video uri. Body: $POLL_BODY" >&2
      exit 1
    fi
    break
  fi
done

if [ -z "$VIDEO_URI" ]; then
  echo "ERROR: timeout waiting for veo (5min). Op: $OP_NAME" >&2
  exit 124
fi

DL_URL="${VIDEO_URI}"
case "$DL_URL" in
  *\?*) DL_URL="${DL_URL}&key=${GOOGLE_API_KEY}" ;;
  *) DL_URL="${DL_URL}?key=${GOOGLE_API_KEY}" ;;
esac

echo "[veo] downloading to $OUTPUT_PATH ..."
curl -sS -L -o "$OUTPUT_PATH" "$DL_URL"

SIZE_KB="$(du -k "$OUTPUT_PATH" | cut -f1)"
echo "---"
echo "OUTPUT:    $OUTPUT_PATH"
echo "SIZE:      ${SIZE_KB} KB"
echo "DURATION:  ~8s"
echo "RES:       720p (Fast tier)"
echo "COST_EST:  \$0.80 (8s @ 720p Fast)"
echo "---"
