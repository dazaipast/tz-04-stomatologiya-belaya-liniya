(function () {
  "use strict";

  var PARAMS = {
    cta_click: ["button_name", "page_section"],
    service_view: ["service_name"],
    select_service: ["service_name", "price_from"],
    doctor_view: ["doctor_id", "specialty"],
    doctor_filter: ["specialty"],
    price_search: ["search_term", "results_count"],
    promo_copy: ["promo_code"],
    contact_click: ["contact_type"],
    messenger_click: ["messenger"],
    social_click: ["network", "page_section"],
    form_error: ["field_name", "error_type"],
    generate_lead: ["lead_service", "lead_source"],
    map_open: ["map_service"],
    license_open: ["page_section"]
  };

  function clip(value) {
    return String(value).slice(0, 100);
  }

  function send(name, params) {
    if (typeof gtag !== "function") return;
    var allowed = PARAMS[name] || [];
    var payload = {};
    allowed.forEach(function (key) {
      if (!params || params[key] === undefined || params[key] === null || params[key] === "") return;
      payload[key] = clip(params[key]);
    });
    gtag("event", name, payload);
  }

  function datasetKey(key) {
    return key.replace(/_([a-z])/g, function (_, letter) {
      return letter.toUpperCase();
    });
  }

  function readParams(el, name) {
    var params = {};
    (PARAMS[name] || []).forEach(function (key) {
      var value = el.dataset[datasetKey(key)];
      if (value) params[key] = value;
    });
    return params;
  }

  function copyWithFallback(text) {
    return new Promise(function (resolve, reject) {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.left = "-999px";
      document.body.appendChild(area);
      area.select();
      try {
        if (!document.execCommand("copy")) reject(new Error("copy"));
        else resolve();
      } catch (error) {
        reject(error);
      } finally {
        document.body.removeChild(area);
      }
    });
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(function () {
        return copyWithFallback(text);
      });
    }
    return copyWithFallback(text);
  }

  document.addEventListener("click", function (event) {
    var el = event.target.closest("[data-event]");
    if (!el) return;
    var name = el.getAttribute("data-event");
    if (!PARAMS[name] || name === "price_search" || name === "form_error" || name === "generate_lead") return;

    if (name === "promo_copy") {
      event.preventDefault();
      var code = el.getAttribute("data-promo-code") || "CHECK500";
      copyText(code).then(function () {
        var label = el.querySelector("[data-copy-label]");
        if (label) label.textContent = "Скопировано";
        var status = document.querySelector("[data-copy-status]");
        if (status) status.textContent = "Промокод CHECK500 скопирован.";
      }).catch(function () {
        var status = document.querySelector("[data-copy-status]");
        if (status) status.textContent = "Не удалось скопировать. Промокод CHECK500.";
      });
      send(name, { promo_code: code });
      return;
    }

    send(name, readParams(el, name));
  });

  var priceInput = document.querySelector("[data-event='price_search']");
  if (priceInput) {
    var priceTimer = 0;
    priceInput.addEventListener("input", function () {
      window.clearTimeout(priceTimer);
      priceTimer = window.setTimeout(function () {
        var term = priceInput.value.trim();
        if (!term) return;
        var count = 0;
        document.querySelectorAll("[data-price-row]").forEach(function (row) {
          if (!row.hidden) count += 1;
        });
        send("price_search", {
          search_term: term,
          results_count: String(count)
        });
      }, 1000);
    });
  }

  window.blTrack = send;
})();
