(function () {
  "use strict";

  var filterButtons = document.querySelectorAll("[data-event='doctor_filter']");
  var doctorCards = document.querySelectorAll("[data-doctor-card]");
  filterButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var specialty = button.getAttribute("data-specialty");
      filterButtons.forEach(function (item) {
        item.setAttribute("aria-pressed", item === button ? "true" : "false");
      });
      doctorCards.forEach(function (card) {
        var match = specialty === "все" || card.getAttribute("data-specialty") === specialty;
        card.hidden = !match;
      });
    });
  });

  var priceInput = document.querySelector("[data-price-search]");
  if (priceInput) {
    var rows = document.querySelectorAll("[data-price-row]");
    var empty = document.querySelector("[data-price-empty]");
    var countNode = document.querySelector("[data-price-count]");
    var filterRows = function () {
      var term = priceInput.value.trim().toLocaleLowerCase("ru");
      var count = 0;
      rows.forEach(function (row) {
        var haystack = (row.getAttribute("data-search") || "").toLocaleLowerCase("ru");
        var match = !term || haystack.indexOf(term) !== -1;
        row.hidden = !match;
        if (match) count += 1;
      });
      if (empty) empty.hidden = count !== 0;
      if (countNode) countNode.textContent = "Показано " + count + " из " + rows.length;
    };
    priceInput.addEventListener("input", filterRows);
    filterRows();
  }

  var requestNode = document.querySelector("[data-request-id]");
  if (requestNode) {
    var requestId = new URLSearchParams(window.location.search).get("id") || "";
    if (/^REQ-[0-9a-f-]{36}$/i.test(requestId)) {
      requestNode.textContent = requestId;
    } else {
      requestNode.textContent = "Номер появится после отправки формы";
    }
  }
})();
