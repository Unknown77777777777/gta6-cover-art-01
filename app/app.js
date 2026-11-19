// GTA VI Cover Studio — all client-side. Draws the uploaded photo with a
// sunset / neon / beach grade, a GTA VI title block, and exports PNG.
const canvas = document.getElementById('cover');
const ctx = canvas.getContext('2d');
let photo = null;
let preset = 'sunset';
const PRESETS = {
  sunset: { top: '#1a0840', mid: '#ff5e62', low: '#ffb042', tint: 'rgba(255,120,60,0.18)' },
  neon: { top: '#050510', mid: '#7b2ff7', low: '#00e5ff', tint: 'rgba(123,47,247,0.22)' },
  beach: { top: '#0b5e7a', mid: '#37b6ff', low: '#ffe9a8', tint: 'rgba(55,182,255,0.15)' },
};
function draw(w, h) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d');
  const p = PRESETS[preset];
  const grad = g.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, p.top); grad.addColorStop(0.6, p.mid); grad.addColorStop(1, p.low);
  g.fillStyle = grad; g.fillRect(0, 0, w, h);
  if (photo) {
    const s = Math.max(w / photo.width, h / photo.height);
    const dw = photo.width * s, dh = photo.height * s;
    g.drawImage(photo, (w - dw) / 2, (h - dh) / 2, dw, dh);
    g.fillStyle = p.tint; g.fillRect(0, 0, w, h);
  } else {
    g.fillStyle = '#ffd682'; g.beginPath();
    g.arc(w * 0.68, h * 0.34, w * 0.13, 0, Math.PI * 2); g.fill();
    g.fillStyle = 'rgba(10,8,30,0.9)';
    for (let x = 0; x < w; x += w / 9) g.fillRect(x, h * 0.55, w / 12, h * 0.13);
  }
  g.fillStyle = 'rgba(0,0,0,0.45)'; g.fillRect(0, 0, w, h * 0.10);
  g.fillStyle = '#fff'; g.font = `bold ${Math.round(w * 0.028)}px Arial`;
  g.fillText('ROCKSTAR  •  VICE CITY', w * 0.04, h * 0.06);
  const title = document.getElementById('title').value || 'GRAND THEFT AUTO VI';
  const tag = document.getElementById('tagline').value || 'VICE CITY  •  2026';
  g.textAlign = 'center';
  g.font = `bold ${Math.round(w * 0.11)}px Arial`;
  g.lineWidth = Math.max(3, w * 0.004); g.strokeStyle = '#000';
  const lines = title.split(' ');
  const mid = Math.ceil(lines.length / 2);
  const l1 = lines.slice(0, mid).join(' '), l2 = lines.slice(mid).join(' ') || 'VI';
  g.strokeText(l1, w / 2, h * 0.78); g.fillStyle = '#fff'; g.fillText(l1, w / 2, h * 0.78);
  g.strokeText(l2, w / 2, h * 0.88); g.fillText(l2, w / 2, h * 0.88);
  g.fillStyle = '#ffc400'; g.font = `bold ${Math.round(w * 0.032)}px Arial`;
  g.fillText(tag, w / 2, h * 0.94);
  return c;
}
function render() {
  const c = draw(1080, 1080);
  ctx.clearRect(0, 0, 1080, 1080); ctx.drawImage(c, 0, 0);
}
document.getElementById('photo').addEventListener('change', (e) => {
  const f = e.target.files[0]; if (!f) return;
  const img = new Image();
  img.onload = () => { photo = img; render(); };
  img.src = URL.createObjectURL(f);
});
document.querySelectorAll('[data-preset]').forEach((b) => b.addEventListener('click', () => {
  preset = b.dataset.preset;
  document.querySelectorAll('[data-preset]').forEach((x) => x.classList.toggle('active', x === b));
  render();
}));
document.querySelectorAll('[data-export]').forEach((b) => b.addEventListener('click', () => {
  const [w, h] = b.dataset.export.split('x').map(Number);
  draw(w, h).toBlob((blob) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `gta6-cover-${w}x${h}.png`; a.click();
  }, 'image/png');
}));
['title', 'tagline'].forEach((id) => document.getElementById(id).addEventListener('input', render));
render();
