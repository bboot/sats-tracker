$(document).ready(function(){
  tx_lookup();
  $(".tx-lookup").click(tx_lookup);
});

tx_lookup = () => {
  let addr = $('input[name="address"]').val();
  let amount = $('input[name="amount"]').val();
  let txid = $('input[name="transaction"]').val();
  $.post("/api/tx_lookup", {
         "address": addr,
         "amount": amount,
         "txid": txid,
         "csrfmiddlewaretoken": csrftoken,
    }, function(data, status){
    //alert("Data: " + data + "\nStatus: " + status);
    let info  = JSON.parse(data);
    if ('data' in info) {
      populate_tx_candidates(info.data);
    } else {
      alert("Unknown response.");
    }
  }).fail(function(response){
    alert("Server reported an error.");
  });
}

populate_fields = function(data){
  document.getElementById("id_transaction").value = data.tx.txid;
  try {
    document.getElementById("id_height").value = data.tx.height + "";
  } catch(err) {
    // not on this page
  }
  if (!Number.isNaN(data.amount)) {
    document.getElementById("id_amount").value = data.tx.amount + "";
  } else {
    document.getElementById("id_amount").value = "0";
  }
  if (data.spent_tx) {
    document.getElementById("id_spent_tx").value = data.spent_tx;
  }
  if (document.getElementById("id_address").value) {
    if (document.getElementById("id_address").value != data.address) {
      alert("Address mismatch!");
    }
  }
  document.getElementById("id_address").value = data.address;
}

populate_tx_candidates = function(data){
  if (Object.keys(data).length == 0) {
    return;
  }
  let candidates = data.transactions
  let table = document.getElementById('transactions-body');
  let nrows = table.rows.length;
  for (let i=nrows-1; i>=0; i--) {
    table.deleteRow(i);
  }
  let amount = document.getElementById("id_amount").value;
  let txid = document.getElementById("id_transaction").value;
  candidates.forEach(function(tx, index, candidates) {
    let row = table.insertRow(index);
    let cell_tx = row.insertCell(0);
    let cell_blockheight = row.insertCell(1);
    let cell_value = row.insertCell(2);
    cell_tx.innerHTML = tx.txid;
    if (tx.match && ((amount && tx.amount == amount) || (tx && tx.txid == txid))) {
      cell_tx.innerHTML = tx.txid + '<i class="fas fa-arrow-left"></i>';
    }
    cell_blockheight.innerHTML = tx.height;
    let n = parseInt(tx.amount);
    let value = n.toLocaleString("en-US");
    cell_value.innerHTML = value + "$";
    row.id = tx.txid
    row.onclick = function(mouse_click){
      populate_fields({ "tx": tx, "spent_tx": data.spent_tx, "address": data.address });
    }
  })
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');
