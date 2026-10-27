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

  document.querySelectorAll("[data-slider]").forEach(function (root) {
    var viewport = root.querySelector(".slider__viewport");
    var track = root.querySelector(".slider__track");
    var real = Array.prototype.slice.call(track.children);
    var total = real.length;
    var count = root.querySelector("[data-slider-count]");
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!viewport || !track || total < 2) return;

    function stripClone(node) {
      node.querySelectorAll("[id]").forEach(function (el) {
        el.removeAttribute("id");
      });
      node.querySelectorAll("[data-event]").forEach(function (el) {
        el.removeAttribute("data-event");
      });
      node.setAttribute("aria-hidden", "true");
      node.querySelectorAll("a, button").forEach(function (el) {
        el.tabIndex = -1;
      });
    }

    var firstClone = real[0].cloneNode(true);
    var lastClone = real[total - 1].cloneNode(true);
    stripClone(firstClone);
    stripClone(lastClone);
    track.insertBefore(lastClone, real[0]);
    track.appendChild(firstClone);

    var index = 1;
    var hash = (window.location.hash || "").replace(/^#/, "");
    if (hash) {
      real.forEach(function (slide, slideIndex) {
        var selector = window.CSS && CSS.escape ? "#" + CSS.escape(hash) : '[id="' + hash + '"]';
        if (slide.querySelector(selector)) index = slideIndex + 1;
      });
    }

    function realIndex() {
      if (index === 0) return total - 1;
      if (index === total + 1) return 0;
      return index - 1;
    }

    function setFocusable() {
      var current = realIndex();
      real.forEach(function (slide, slideIndex) {
        var active = slideIndex === current;
        slide.setAttribute("aria-hidden", active ? "false" : "true");
        slide.querySelectorAll("a, button").forEach(function (el) {
          if (active) el.removeAttribute("tabindex");
          else el.setAttribute("tabindex", "-1");
        });
      });
    }

    function move(animate) {
      var width = viewport.clientWidth;
      Array.prototype.forEach.call(track.children, function (slide) {
        slide.style.flexBasis = width + "px";
        slide.style.width = width + "px";
      });
      if (!animate || reduce) track.classList.add("is-instant");
      track.style.transform = "translate3d(" + -index * width + "px,0,0)";
      if (!animate || reduce) {
        track.getBoundingClientRect();
        track.classList.remove("is-instant");
      }
      if (count) count.textContent = realIndex() + 1 + " из " + total;
      setFocusable();
    }

    function settle() {
      if (index === 0) index = total;
      else if (index === total + 1) index = 1;
      else return;
      move(false);
    }

    track.addEventListener("transitionend", function (event) {
      if (event.target !== track || event.propertyName !== "transform") return;
      settle();
    });

    function go(delta) {
      index += delta;
      move(true);
      if (reduce) settle();
    }

    root.querySelector("[data-slider-prev]").addEventListener("click", function () {
      go(-1);
    });
    root.querySelector("[data-slider-next]").addEventListener("click", function () {
      go(1);
    });

    var startX = 0;
    var startY = 0;
    var tracking = false;
    var swiped = false;
    viewport.addEventListener("pointerdown", function (event) {
      if (event.pointerType === "mouse" && event.button !== 0) return;
      tracking = true;
      swiped = false;
      startX = event.clientX;
      startY = event.clientY;
    });
    viewport.addEventListener("pointerup", function (event) {
      if (!tracking) return;
      tracking = false;
      var dx = event.clientX - startX;
      var dy = event.clientY - startY;
      if (Math.abs(dx) < 48 || Math.abs(dx) < Math.abs(dy)) return;
      swiped = true;
      go(dx < 0 ? 1 : -1);
    });
    viewport.addEventListener("click", function (event) {
      if (!swiped) return;
      event.preventDefault();
      event.stopPropagation();
      swiped = false;
    }, true);

    root.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      if (event.target.closest("input, select, textarea")) return;
      event.preventDefault();
      go(event.key === "ArrowRight" ? 1 : -1);
    });

    window.addEventListener("resize", function () {
      move(false);
    });

    move(false);
  });

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
