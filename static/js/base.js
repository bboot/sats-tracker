$(document).ready(() => {
  const urlParams = new URLSearchParams(window.location.search);
  const highlighted = urlParams.get("hl");
  if (highlighted) {
    let card = document.getElementById(highlighted);
    card.scrollIntoView({
              behavior: 'auto',
              block: 'center',
              inline: 'center'
    });
    card.classList.add("blink-me");
    setTimeout(() => {
      card.classList.remove("blink-me");
    }, 1000);
  }
});

