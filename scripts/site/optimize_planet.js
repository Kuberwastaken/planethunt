/* Encoding and responsive sizes only; generated originals are preserved. Requires sharp. */
const sharp=require('sharp');
(async()=>{for(const name of ['exterior','atmosphere','interior','system']){
 await sharp(`docs/planet/${name}.png`).webp({quality:88}).toFile(`docs/planet/${name}.webp`);
 await sharp(`docs/planet/${name}.png`).resize(724,543).webp({quality:85}).toFile(`docs/planet/${name}-724.webp`);
}})();
