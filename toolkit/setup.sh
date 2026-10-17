#!/usr/bin/env bash
# Baut die mw/-Arbeitsstruktur aus diesem Repo auf: bash toolkit/setup.sh <slug>
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"; MW="${MW:-$HOME/mw}"; SLUG="${1:-video}"
mkdir -p "$MW"/{robot3,brand/out,thumb,"$SLUG"}
cp "$REPO/toolkit/robot_soft.py" "$MW/robot3/soft.py"
cp "$REPO/toolkit/missionwissen-logo-transparent-dunkel.svg" "$MW/brand/out/"
cp "$REPO/toolkit/"{dyn_ws.py,storyboard.py,renderall.py,sfx.py} "$MW/$SLUG/"
cp "$REPO/toolkit/build_fz.py" "$MW/$SLUG/build.py"
cp "$REPO/toolkit/thumb_fz.py" "$MW/$SLUG/thumb.py"
if [ ! -d "$MW/fonts/gf/ofl/unbounded" ]; then
  mkdir -p "$MW/fonts" && cd "$MW/fonts"
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/google/fonts gf
  cd gf && git sparse-checkout set ofl/unbounded ofl/inter ofl/jetbrainsmono
fi
echo "bereit: $MW/$SLUG (build.py = Vorlage Führungszeugnis; CH, B, Szenen ersetzen; Wortzeiten nach ws.json)"
