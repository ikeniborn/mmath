# Theme assets

Every picture in `themes/` is drawn by hand for this repository as plain SVG primitives (circles, rectangles, paths) and is licensed together with the repository. No third-party artwork, font or icon set is included or fetched; nothing is loaded from a CDN.

- `themes/shapes.tsx` — four objects per theme (flowers: daisy, tulip, sunflower, leaf; dolls: doll, bow, bear, balloon; cars: car, bus, truck, bike; construction: excavator, cone, crane, brick) and the badge palette.
- `themes/index.tsx` — `ThemeIcon` (one object), `Shape` (circle, square, triangle, star for the pick tasks) and `Sticker` (an object on a circle or star badge; codes `<theme>-<1..8>`).

Scenes (basket, garage, train carriages, tray) are CSS shapes in `features/game/TaskPicture.module.css` and `features/game/early/Early.module.css`.
