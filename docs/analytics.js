(() => {
  const endpoint = "https://jintai-kittie.goatcounter.com/count";
  if (!endpoint || window.location.hostname !== "jintaili.github.io") return;

  const pagePath = window.location.pathname.replace(/\/index\.html$/, "/");
  window.goatcounter = { path: pagePath };
  const pending = [];

  // Count the first play of each video per page load, including early plays
  // while the analytics script is still downloading.
  document.querySelectorAll("video").forEach((video) => {
    video.addEventListener("play", () => {
      const source = video.getAttribute("src") ||
        video.querySelector("source")?.getAttribute("src");
      if (!source) return;
      const mediaPath = new URL(source, window.location.href).pathname;
      const label = video.getAttribute("aria-label") ||
        video.closest("article")?.querySelector("h3")?.textContent || mediaPath;
      const event = {
        path: `video-play:${pagePath}:${mediaPath}`,
        title: `Video play: ${label}`,
        event: true,
      };
      if (typeof window.goatcounter.count === "function") {
        window.goatcounter.count(event);
      } else {
        pending.push(event);
      }
    }, { once: true });
  });

  const script = document.createElement("script");
  script.async = true;
  script.src = "https://gc.zgo.at/count.js";
  script.setAttribute("data-goatcounter", endpoint);
  script.onload = () => {
    if (typeof window.goatcounter.count !== "function") return;
    pending.forEach((event) => window.goatcounter.count(event));
    pending.length = 0;
  };
  document.head.appendChild(script);
})();
