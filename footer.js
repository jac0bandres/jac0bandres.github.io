async function loadFooter() {
  const res = await fetch("/footer.html");
  const html = await res.text();
  document.body.insertAdjacentHTML("beforeend", html);
}
loadFooter();
