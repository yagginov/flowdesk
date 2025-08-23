const scrollBox = document.getElementById("lists-scroll");
const scrollbar = document.getElementById("lists-scrollbar");

function syncScrollbar() {
  const visible = scrollBox.clientWidth;
  const full = scrollBox.scrollWidth;
  const track = scrollbar.offsetWidth;

  const thumbWidth = Math.max((visible / full) * track, 50);

  scrollbar.style.setProperty("--thumb-width", `${thumbWidth}px`);

  scrollbar.max = full - visible;
  scrollbar.value = scrollBox.scrollLeft;
}

scrollBox.addEventListener("scroll", () => {
  scrollbar.value = scrollBox.scrollLeft;
});
scrollbar.addEventListener("input", () => {
  scrollBox.scrollLeft = scrollbar.value;
});

window.addEventListener("load", syncScrollbar);
window.addEventListener("resize", syncScrollbar);
