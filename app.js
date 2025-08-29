const repo = "jac0bandres/jacobandres.com";
const path = "blog"; // folder where .md posts live

async function loadPosts() {
  const res = await fetch(`https://api.github.com/repos/${repo}/contents/${path}`);
  const files = await res.json();

  const container = document.getElementById("posts");
  container.innerHTML = ""; // clear loading text

  for (let file of files) {
    if (file.name.endsWith(".md")) {
      const mdRes = await fetch(file.download_url);
      const mdText = await mdRes.text();
      const html = marked.parse(mdText);

      const article = document.createElement("article");
      article.innerHTML = `<h2>${file.name.replace(".md", "")}</h2>` + html;
      container.appendChild(article);
    }
  }
}

if (document.getElementById("posts")) {
  loadPosts();
}

