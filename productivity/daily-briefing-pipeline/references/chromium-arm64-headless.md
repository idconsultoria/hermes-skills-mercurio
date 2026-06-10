# Chromium Headless on ARM64 (no root)

## Context

Debian 13 (trixie), aarch64, no root. Google's official Chromium builds don't ship for Linux ARM64. Playwright downloads require glibc >= 2.42; this system has 2.41. Solution: use Debian's chromium package via `.deb` extraction.

## Setup (one-time)

```bash
cd /tmp
apt-get download chromium chromium-common libdouble-conversion3 libharfbuzz-subset0 libminizip1t64 libopenh264-8 libicu76
mkdir -p chromium-extracted
for pkg in chromium_*.deb chromium-common_*.deb; do dpkg -x "$pkg" chromium-extracted/; done
for pkg in lib*.deb; do dpkg -x "$pkg" chromium-extracted/; done
cp chromium-extracted/usr/lib/aarch64-linux-gnu/*.so* chromium-extracted/usr/lib/chromium/
```

## Generate PDF

```bash
CHROMIUM=/tmp/chromium-extracted/usr/lib/chromium/chromium
LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium

$CHROMIUM --headless --no-sandbox --disable-gpu \
  --print-to-pdf="/tmp/output.pdf" "file:///tmp/input.html"
```

## Critical: icudtl.dat

The `chromium-common` package provides `icudtl.dat` (11 MB). Without it, the binary crashes with `ERROR:base/i18n/icu_util.cc:232] Invalid file descriptor to ICU data received`.

## Harmless Errors

DBus errors (`Failed to connect to the bus`) are normal in headless/server environments and don't affect PDF output.
