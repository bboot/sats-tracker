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
    let on = document.getElementsByClassName(name + "-on")[0];
    let off = document.getElementsByClassName(name + "-off")[0];
    let state;
    if (on.style.display == "none" || on.style.display == "") {
        on.style.display = "block";
        off.style.display = "none";
        state = true; // filter is on
    } else {
        on.style.display = "none";
        off.style.display = "block";
        state = false; // filter is off
    }
    //toggle_filter(name, state);
}


class FilterStates {
    static filter_states = {
        "key-filter": false,
        "spent-filter": false,
    }

    static state() {
        for (let key in FilterStates.filter_states) {
            if (!FilterStates.filter_states[key]) {
                return false;
            }
        }
        return true;
    }
}

toggle_filter = (name, state) => {
    FilterStates.filter_states[name] = state;
    const filtered = document.getElementsByClassName(name);
    const array = Array.from(filtered);
    array.forEach((item) => {
        parents = [...(function*(e){while (e = e.parentNode) { yield e; }})(item)]
        if (FilterStates.state()) {
            // filter is off, so it should not be filtered
            parents[5].style.display = "block";
        } else {
            // filter is on, so it should be filtered out
            parents[5].style.display = "none";
        }
    });
}
