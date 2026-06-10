# Chromium Headless on ARM64 (no root)

## Context

This environment is **Debian 13 (trixie), aarch64, no root**. Google's official Chromium builds don't ship for Linux ARM64. Playwright can download a build, but it requires glibc >= 2.42 while this system has 2.41. The solution: use Debian's own `chromium` package from `apt` by downloading the `.deb` and extracting it.

## Full Setup

```bash
cd /tmp

# 1. Download packages
apt-get download chromium chromium-common

# 2. Create extraction directory
mkdir -p chromium-extracted

# 3. Extract chromium and its common data
for pkg in chromium_*.deb chromium-common_*.deb; do
  dpkg -x "$pkg" chromium-extracted/
done

# 4. Download and extract dependencies
apt-get download libdouble-conversion3 libharfbuzz-subset0 \
  libminizip1t64 libopenh264-8 libicu76

for pkg in lib*.deb; do
  dpkg -x "$pkg" chromium-extracted/
done

# 5. Consolidate all shared libraries into one directory
cp chromium-extracted/usr/lib/aarch64-linux-gnu/*.so* \
  chromium-extracted/usr/lib/chromium/
```

## Generate PDF

```bash
CHROMIUM=/tmp/chromium-extracted/usr/lib/chromium/chromium
LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium

$CHROMIUM --headless --no-sandbox --disable-gpu \
  --print-to-pdf="/tmp/output.pdf" \
  "file:///tmp/input.html"
```

## Critical File

The `chromium-common` package provides `icudtl.dat` (11 MB) in `/usr/lib/chromium/`. Without this file the binary crashes immediately with:
```
ERROR:base/i18n/icu_util.cc:232] Invalid file descriptor to ICU data received.
```

## Known Harmless Errors

```
ERROR:dbus/bus.cc:405] Failed to connect to the bus: No such file or directory
GLib-GIO-CRITICAL **: g_settings_schema_source_lookup: assertion 'source != NULL' failed
```

These occur because the server has no desktop environment (no D-Bus). They don't affect PDF output.

## Why Not Playwright

Playwright's install command (`playwright install chromium`) downloads Google's official build, which requires glibc >= 2.42. Our Debian 13 trixie system has glibc 2.41. Additionally, `playwright install --with-deps chromium` tries to `su` to root to install system dependencies, which fails.

The Debian-packaged chromium is compiled for glibc 2.41 and works perfectly when extracted.
