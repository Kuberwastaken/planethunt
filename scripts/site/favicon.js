/* Render the same code-native planetary mark at browser and touch-icon sizes.
   Requires sharp. SVG source remains editable and is also used directly by browsers. */
const fs=require('fs');
const sharp=require('sharp');
const svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><title>Planethunt planet</title><rect width="64" height="64" rx="12" fill="#050505"/><circle cx="32" cy="32" r="24" fill="#f4f4f4"/><path d="M32 8a24 24 0 0 1 0 48c15-9 15-39 0-48Z" fill="#545454"/><path d="M12 23c7-5 16-5 22-2M9 33c9-5 19-5 27-1M15 44c8-3 14-3 19-1" fill="none" stroke="#b0b0b0" stroke-width="2.5"/></svg>';
fs.writeFileSync('docs/favicon.svg',svg+'\n');
(async()=>{
for(const size of [32,48,180,192,512])await sharp(Buffer.from(svg)).resize(size,size).png().toFile(`docs/favicon-${size}.png`);
const png=fs.readFileSync('docs/favicon-32.png');const header=Buffer.alloc(22);header.writeUInt16LE(1,2);header.writeUInt16LE(1,4);header[6]=32;header[7]=32;header.writeUInt16LE(1,10);header.writeUInt16LE(32,12);header.writeUInt32LE(png.length,14);header.writeUInt32LE(22,18);fs.writeFileSync('favicon.ico',Buffer.concat([header,png]));
})();
