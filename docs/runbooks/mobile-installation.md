# Mobile installation (connected PWA)

The web app installs as a standalone app on phones and works only while connected: the service worker precaches the public shell (offline page, manifest, icons, hashed assets) and never caches `/api`, authentication responses or any child data. There is no offline arithmetic and no background answer queue; an answer that could not be sent stays in the tab's pending record until the parent or child presses Retry.

## Requirements

- Public mode over HTTPS (`mmath.ikeniborn.ru` through the external Traefik). LAN HTTP mode stays an ordinary website: browsers do not install or register service workers on plain HTTP except loopback.
- Android: Chromium-based browsers offer "Install app" from the menu or an install banner. iOS: Safari, Share → "Add to Home Screen". Other browsers may not support installation.

## Behaviour to verify on a real device

1. Install from the public host; the icon and the name "Считай легко" appear; launch opens in standalone mode.
2. Sign in, pick a child, answer a task; the flow matches the web journey.
3. Turn off connectivity, launch the installed app: the "Connection required" page appears without any previous child name, and Retry recovers once connected.
4. Sign out, go offline, launch: still no child data.
5. After a new release, open the app on the child home screen: an "update available" banner appears only there or on the parent screens, never mid-answer; accepting it reloads once.

Record the device model, OS version and browser version in `release-checklist.md`. Desktop WebKit emulation is not evidence of iOS installation.

## Edge cache headers

The edge serves `/assets/*` as immutable for a year (hashed file names), and `sw.js`, the manifest and HTML with `no-cache` so a new release is picked up on the next visit.
