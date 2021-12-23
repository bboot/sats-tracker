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

toggle_icon = (name) => {
    let icon = document.getElementsByClassName(name)[0];
    let slash_icon = document.getElementsByClassName("slash-" + name)[0];
    if (slash_icon.style.display == "none") {
        slash_icon.style.display = "block";
        icon.style.display = "none";
    } else {
        slash_icon.style.display = "none";
        icon.style.display = "block";
    }
}
