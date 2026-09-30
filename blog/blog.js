(() => {
  const canvas = document.getElementById('complex-plane');
  if (!canvas) return;
  const context = canvas.getContext('2d');
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let width = 0;
  let height = 0;
  let frame = 0;

  function point(x, y, progress) {
    const pole = -1 + progress * 2;
    const dx = x - pole;
    const radius = dx * dx + y * y + .06;
    const strength = .3 + .24 * Math.sin(progress * Math.PI);
    return { x: x + strength * dx / radius, y: y - strength * y / radius };
  }

  function draw() {
    frame = 0;
    context.clearRect(0, 0, width, height);
    const travel = Math.max(1, document.documentElement.scrollHeight - height);
    const progress = reduceMotion ? .35 : Math.min(1, scrollY / travel);
    const scale = Math.min(width, height) / 4.8;

    for (let index = -16; index <= 16; index++) {
      for (const vertical of [true, false]) {
        context.beginPath();
        let previous = null;
        for (let step = 0; step <= 180; step++) {
          const variable = -4 + step * (8 / 180);
          const value = index * .25;
          const mapped = point(vertical ? value : variable, vertical ? variable : value, progress);
          const px = width / 2 + mapped.x * scale;
          const py = height / 2 - mapped.y * scale;
          const jump = previous && Math.hypot(px - previous[0], py - previous[1]) > width * .22;
          if (!previous || jump) context.moveTo(px, py);
          else context.lineTo(px, py);
          previous = [px, py];
        }
        const axis = index === 0;
        context.strokeStyle = axis ? 'rgba(226,187,63,.62)' : index % 4 === 0 ? 'rgba(158,183,136,.3)' : 'rgba(126,151,145,.16)';
        context.lineWidth = axis ? 1.5 : 1;
        context.stroke();
      }
    }
  }

  function resize() {
    const ratio = Math.min(devicePixelRatio || 1, 2);
    width = innerWidth;
    height = innerHeight;
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    draw();
  }

  addEventListener('resize', resize);
  addEventListener('scroll', () => {
    if (!frame) frame = requestAnimationFrame(draw);
  }, { passive: true });
  resize();
})();
