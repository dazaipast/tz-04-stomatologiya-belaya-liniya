(function () {
  "use strict";

  var form = document.querySelector("#lead-form");
  if (!form) return;

  var SERVICES = ["consult", "hygiene", "treatment", "implant", "braces", "kids"];
  var TIMES = ["morning", "day", "evening", "weekend"];
  var alertBox = document.querySelector("#form-alert");
  var submitButton = form.querySelector("[type='submit']");

  function makeId() {
    if (window.crypto && crypto.randomUUID) return "REQ-" + crypto.randomUUID();
    return "REQ-" + "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (char) {
      var rand = Math.random() * 16 | 0;
      var value = char === "x" ? rand : (rand & 0x3 | 0x8);
      return value.toString(16);
    });
  }

  form.elements.request_id.value = makeId();

  var preset = new URLSearchParams(window.location.search).get("service");
  if (SERVICES.indexOf(preset) !== -1) form.elements.service.value = preset;

  function normalizePhone(value) {
    var digits = String(value).replace(/\D/g, "");
    if (digits.length === 11 && (digits.charAt(0) === "7" || digits.charAt(0) === "8")) {
      return "+7" + digits.slice(1);
    }
    if (digits.length === 10) return "+7" + digits;
    return "";
  }

  function setError(fieldName, message) {
    var field = form.querySelector("[data-field='" + fieldName + "']");
    if (!field) return;
    field.classList.add("is-invalid");
    field.querySelectorAll("input, select").forEach(function (input) {
      input.setAttribute("aria-invalid", "true");
    });
    var error = field.querySelector(".field-error");
    if (error) error.textContent = message;
  }

  function clearErrors() {
    form.querySelectorAll(".is-invalid").forEach(function (field) {
      field.classList.remove("is-invalid");
      field.querySelectorAll("input, select").forEach(function (input) {
        input.removeAttribute("aria-invalid");
      });
    });
    form.querySelectorAll(".field-error").forEach(function (node) {
      node.textContent = "";
    });
    if (alertBox) {
      alertBox.hidden = true;
      alertBox.textContent = "";
    }
  }

  function trackError(fieldName, errorType) {
    if (window.blTrack) window.blTrack("form_error", { field_name: fieldName, error_type: errorType });
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    clearErrors();

    var name = form.elements.name.value.trim();
    var phoneRaw = form.elements.phone.value.trim();
    var email = form.elements.email.value.trim();
    var service = form.elements.service.value;
    var preferredTime = form.elements.preferred_time.value;
    var consent = form.elements.consent.checked;
    var phone = normalizePhone(phoneRaw);
    var errors = [];

    if (name.length < 2 || name.length > 60) {
      errors.push(["name", "required", "Введите имя: от 2 до 60 символов."]);
    }
    if (!phoneRaw) errors.push(["phone", "required", "Введите телефон."]);
    else if (!phone) errors.push(["phone", "format", "Телефон укажите в формате +7 и ещё 10 цифр."]);
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.push(["email", "format", "Проверьте написание e-mail или оставьте поле пустым."]);
    }
    if (SERVICES.indexOf(service) === -1) errors.push(["service", "required", "Выберите услугу."]);
    if (TIMES.indexOf(preferredTime) === -1) errors.push(["preferred_time", "required", "Выберите удобное время."]);
    if (!consent) errors.push(["consent", "required", "Нужно согласие на обработку персональных данных."]);

    if (errors.length) {
      errors.forEach(function (item) {
        setError(item[0], item[2]);
        trackError(item[0], item[1]);
      });
      if (alertBox) {
        alertBox.hidden = false;
        alertBox.textContent = "Заявка не отправлена. Проверьте выделенные поля.";
      }
      var first = form.querySelector(".is-invalid input, .is-invalid select");
      if (first) first.focus();
      return;
    }

    var utm = window.blUtm ? window.blUtm() : {
      utm_source: "direct",
      utm_medium: "none",
      utm_campaign: "not_set",
      utm_content: "not_set"
    };
    var payload = {
      request_id: form.elements.request_id.value,
      name: name,
      phone: phone,
      email: email,
      service: service,
      preferred_time: preferredTime,
      utm_source: utm.utm_source,
      utm_medium: utm.utm_medium,
      utm_campaign: utm.utm_campaign,
      utm_content: utm.utm_content
    };

    var endpoint = window.BL_CONFIG && window.BL_CONFIG.appsScriptUrl;
    if (!endpoint) {
      setError("phone", "Приём заявок ещё не подключён. Позвоните: +7 (900) 404-04-40.");
      trackError("form", "server");
      if (alertBox) {
        alertBox.hidden = false;
        alertBox.textContent = "Заявка не отправлена: не указан адрес приёмника в js/config.js.";
      }
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Отправляем…";

    fetch(endpoint, {
      method: "POST",
      redirect: "follow",
      body: JSON.stringify(payload)
    }).then(function (response) {
      return response.text();
    }).then(function (text) {
      var data = {};
      try {
        data = JSON.parse(text);
      } catch (error) {
        data = { ok: false, error: "server" };
      }
      if (!data.ok) {
        var fieldName = data.field || "form";
        var errorType = data.error_type || "server";
        setError(fieldName === "form" ? "phone" : fieldName, data.error || "Не удалось отправить заявку. Попробуйте ещё раз или позвоните в клинику.");
        trackError(fieldName, errorType);
        if (alertBox) {
          alertBox.hidden = false;
          alertBox.textContent = data.error || "Сервис заявок не принял форму.";
        }
        submitButton.disabled = false;
        submitButton.textContent = "Отправить заявку";
        return;
      }
      if (window.blTrack) {
        window.blTrack("generate_lead", {
          lead_service: service,
          lead_source: utm.utm_source
        });
      }
      window.location.href = "thanks.html?id=" + encodeURIComponent(payload.request_id);
    }).catch(function () {
      setError("phone", "Не удалось отправить заявку. Проверьте интернет или позвоните в клинику.");
      trackError("form", "server");
      if (alertBox) {
        alertBox.hidden = false;
        alertBox.textContent = "Сервис заявок не ответил.";
      }
      submitButton.disabled = false;
      submitButton.textContent = "Отправить заявку";
    });
  });
})();
