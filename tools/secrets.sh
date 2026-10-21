#!/bin/bash
# Keeps secrets.yaml in Bitwarden: one Secure Note, one hidden custom field per key.
# The same file is /config/esphome/secrets.yaml on HA, shared by every ESPHome device.
#
#   tools/secrets.sh pull     # Bitwarden -> secrets.yaml (mode 600)
#   tools/secrets.sh push     # secrets.yaml -> Bitwarden (creates the note or replaces its fields)
#   tools/secrets.sh check    # compare Bitwarden with secrets.yaml, key names only
#   tools/secrets.sh deploy   # secrets.yaml -> HA /config/esphome/secrets.yaml (old file backed up)
#
# Needs the Bitwarden CLI (brew install bitwarden-cli), `bw login` once, and asks for the master password
# unless BW_SESSION is already set. ITEM overrides the note name.
set -euo pipefail
cd "$(dirname "$0")/.."

ITEM=${ITEM:-ESPHome secrets}
FILE=secrets.yaml

session() {
  if [ -z "${BW_SESSION:-}" ]; then
    BW_SESSION=$(bw unlock --raw)
    export BW_SESSION
  fi
  bw sync >/dev/null
}

# id of the note named exactly $ITEM, empty if none
item_id() {
  bw list items --search "$ITEM" | jq -r --arg n "$ITEM" '[.[] | select(.name == $n)] | .[0].id // empty'
}

# secrets.yaml (flat `key: value` lines) -> Bitwarden fields JSON
yaml_to_fields() {
  /usr/bin/python3 -I -c '
import json, re, sys
fields = []
for line in open(sys.argv[1], encoding="utf-8"):
    m = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.*?)\s*$", line)
    if not m:
        continue
    v = m.group(2)
    if len(v) >= 2 and v[0] == v[-1] == "\"":
        v = json.loads(v)  # also reads what pull writes
    elif len(v) >= 2 and v[0] == v[-1] == "\x27":
        v = v[1:-1].replace("\x27\x27", "\x27")
    elif " #" in v:
        v = v.split(" #", 1)[0].rstrip()
    fields.append({"name": m.group(1), "value": v, "type": 1})
print(json.dumps(fields))
' "$FILE"
}

case "${1:-}" in
  pull)
    session
    id=$(item_id)
    [ -n "$id" ] || { echo "No Bitwarden item named '$ITEM'" >&2; exit 1; }
    umask 077
    {
      echo "# Secrets, referenced from device configs via !secret."
      echo "# Generated from Bitwarden '$ITEM' by tools/secrets.sh pull: edit there, or edit here and push."
      bw get item "$id" | jq -r '.fields[] | "\(.name): \(.value | tojson)"'
    } >"$FILE.tmp"
    mv "$FILE.tmp" "$FILE"
    echo "Wrote $FILE ($(grep -c ': ' "$FILE") keys)"
    ;;
  push)
    [ -f "$FILE" ] || { echo "No $FILE" >&2; exit 1; }
    session
    fields=$(yaml_to_fields)
    id=$(item_id)
    if [ -n "$id" ]; then
      bw get item "$id" | jq --argjson f "$fields" '.fields = $f' | bw encode | bw edit item "$id" >/dev/null
      echo "Updated '$ITEM' ($(jq length <<<"$fields") fields)"
    else
      bw get template item |
        jq --argjson f "$fields" --arg n "$ITEM" \
          '.type = 2 | .secureNote = {type: 0} | .login = null | .name = $n | .fields = $f |
           .notes = "ESPHome secrets.yaml (HA /config/esphome/secrets.yaml). Managed by tools/secrets.sh in github.com/minhkhanh/lich-van-nien."' |
        bw encode | bw create item >/dev/null
      echo "Created '$ITEM' ($(jq length <<<"$fields") fields)"
    fi
    ;;
  check)
    [ -f "$FILE" ] || { echo "No $FILE" >&2; exit 1; }
    session
    id=$(item_id)
    [ -n "$id" ] || { echo "No Bitwarden item named '$ITEM'" >&2; exit 1; }
    # Per key: OK, DIFFERENT, or only on one side. Values are never printed.
    jq -rn --argjson bw "$(bw get item "$id" | jq '.fields // []')" --argjson loc "$(yaml_to_fields)" '
      ($bw | map({(.name): .value}) | add // {}) as $b | ($loc | map({(.name): .value}) | add // {}) as $l |
      (($b | keys) + ($l | keys) | unique)[] as $k |
      if ($b | has($k)) and ($l | has($k)) then
        (if $b[$k] == $l[$k] then "OK         " else "DIFFERENT  " end) + $k
      elif ($b | has($k)) then "only in Bitwarden  " + $k
      else "only in secrets.yaml  " + $k end'
    ;;
  deploy)
    [ -f "$FILE" ] || { echo "No $FILE" >&2; exit 1; }
    ssh hass 'cp /config/esphome/secrets.yaml /config/esphome/secrets.yaml.bak.$(date +%s)'
    scp -q "$FILE" hass:/config/esphome/secrets.yaml
    echo "Copied $FILE to HA (previous file backed up)"
    ;;
  *)
    sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac
