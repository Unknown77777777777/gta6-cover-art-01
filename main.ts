// GTA 6 Cover Art — entry point (Node 22, standard library only).
// Usage:
//   node main.ts                       validate exports + copy to out/
//   MAKEFUN_OUTPUT_DIR=out node main.ts
//   node main.ts --serve [port]        serve app/ as a static site
// Exports are built deterministically by build_cover.py (Pillow, offline).
// main.ts validates PNG magic + exact dimensions, then copies byte-for-byte.
import { createReadStream, createWriteStream, existsSync, mkdirSync, readFileSync, readdirSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { join, extname } from "node:path";

const ROOT = new URL(".", import.meta.url).pathname;
const EXPECTED: Record<string, [number, number]> = {
  "cover-1080x1080.png": [1080, 1080],
  "cover-1080x1350.png": [1080, 1350],
  "cover-1920x1080.png": [1920, 1080],
};

function pngSize(buf: Buffer): [number, number] {
  if (buf.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a") throw new Error("not a PNG");
  return [buf.readUInt32BE(16), buf.readUInt32BE(20)];
}

function validate(): void {
  for (const [name, [w, h]] of Object.entries(EXPECTED)) {
    const p = join(ROOT, "out", name);
    if (!existsSync(p)) throw new Error(`missing export: ${name} — run: python3 build_cover.py`);
    const buf = readFileSync(p);
    const [gw, gh] = pngSize(buf);
    if (gw !== w || gh !== h) throw new Error(`${name}: got ${gw}x${gh}, want ${w}x${h}`);
    console.log(`${name}: OK ${gw}x${gh} ${buf.length} bytes`);
  }
  for (const f of ["app/index.html", "app/styles.css", "app/app.js"]) {
    if (!existsSync(join(ROOT, f))) throw new Error(`missing app file: ${f}`);
  }
  console.log("app/: OK index.html styles.css app.js");
}

function copyOut(): void {
  const dest = process.env.MAKEFUN_OUTPUT_DIR || join(ROOT, "out");
  mkdirSync(dest, { recursive: true });
  for (const name of Object.keys(EXPECTED)) {
    createReadStream(join(ROOT, "out", name)).pipe(createWriteStream(join(dest, name)));
  }
  console.log(`copied exports to ${dest}`);
}

function serve(port: number): void {
  const MIME: Record<string, string> = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".png": "image/png" };
  createServer((req, res) => {
    const path = req.url === "/" ? "/index.html" : (req.url ?? "/index.html");
    const file = join(ROOT, "app", path);
    if (!existsSync(file) || statSync(file).isDirectory()) { res.writeHead(404); res.end("not found"); return; }
    res.writeHead(200, { "Content-Type": MIME[extname(file)] || "application/octet-stream" });
    createReadStream(file).pipe(res);
  }).listen(port, () => console.log(`GTA VI Cover Studio: http://localhost:${port}/`));
}

if (process.argv.includes("--serve")) {
  const port = Number(process.argv[process.argv.indexOf("--serve") + 1] || 8080);
  serve(port);
} else {
  validate();
  copyOut();
}
