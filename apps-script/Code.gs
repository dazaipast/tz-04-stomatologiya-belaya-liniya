var SPREADSHEET_ID = "ВСТАВЬТЕ_ID_ТАБЛИЦЫ";

var SERVICES = ["consult", "hygiene", "treatment", "implant", "braces", "kids"];
var TIMES = ["morning", "day", "evening", "weekend"];
var SERVICE_LABELS = {
  consult: "Консультация",
  hygiene: "Профессиональная гигиена",
  treatment: "Лечение кариеса",
  implant: "Имплантация под ключ",
  braces: "Брекеты",
  kids: "Детский приём"
};
var STAGE_LABELS = {
  new: "New lead",
  contacted: "Contacted",
  appointment: "Appointment booked",
  visited: "Closed won",
  lost: "Closed lost"
};

function doGet() {
  return json({ ok: true, service: "belaya-liniya-leads" });
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(15000);
    var raw = e && e.postData && e.postData.contents ? e.postData.contents : "{}";
    var data = JSON.parse(raw);
    var problem = validateLead(data);
    if (problem) return json({ ok: false, error: problem.error, field: problem.field, error_type: problem.error_type });

    var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName("leads");
    if (!sheet) return json({ ok: false, error: "server", field: "form", error_type: "server" });
    if (hasRequest(sheet, data.request_id)) {
      return json({ ok: false, error: "Заявка с таким номером уже есть", field: "form", error_type: "duplicate" });
    }

    var row = sheet.getLastRow() + 1;
    var values = [[
      data.request_id,
      new Date(),
      data.name,
      "'" + data.phone,
      data.email || "",
      data.service,
      data.preferred_time,
      data.utm_source || "direct",
      data.utm_medium || "none",
      data.utm_campaign || "not_set",
      data.utm_content || "not_set",
      "new"
    ]];
    sheet.getRange(row, 4).setNumberFormat("@");
    sheet.getRange(row, 1, 1, 12).setValues(values);
    return json({ ok: true });
  } catch (error) {
    return json({ ok: false, error: "server", field: "form", error_type: "server" });
  } finally {
    lock.releaseLock();
  }
}

function validateLead(data) {
  if (!data || typeof data !== "object") return problem("form", "server", "server");
  data.name = clip(data.name);
  data.phone = clip(data.phone);
  data.email = clip(data.email);
  data.service = clip(data.service);
  data.preferred_time = clip(data.preferred_time);
  data.request_id = clip(data.request_id);
  data.utm_source = clip(data.utm_source) || "direct";
  data.utm_medium = clip(data.utm_medium) || "none";
  data.utm_campaign = clip(data.utm_campaign) || "not_set";
  data.utm_content = clip(data.utm_content) || "not_set";

  if (!/^REQ-[0-9a-fA-F-]{36}$/.test(data.request_id)) return problem("form", "format", "Некорректный номер заявки");
  if (data.name.length < 2 || data.name.length > 60) return problem("name", "required", "Введите имя: от 2 до 60 символов.");
  if (!/^\+7\d{10}$/.test(data.phone)) return problem("phone", "format", "Телефон укажите в формате +7 и ещё 10 цифр.");
  if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) return problem("email", "format", "Проверьте написание e-mail или оставьте поле пустым.");
  if (SERVICES.indexOf(data.service) === -1) return problem("service", "required", "Выберите услугу.");
  if (TIMES.indexOf(data.preferred_time) === -1) return problem("preferred_time", "required", "Выберите удобное время.");
  return null;
}

function problem(field, errorType, message) {
  return { field: field, error_type: errorType, error: message };
}

function clip(value) {
  return String(value || "").trim().slice(0, 200);
}

function hasRequest(sheet, requestId) {
  var last = sheet.getLastRow();
  if (last < 2) return false;
  var values = sheet.getRange(2, 1, last - 1, 1).getValues();
  for (var i = 0; i < values.length; i++) {
    if (String(values[i][0]) === requestId) return true;
  }
  return false;
}

function json(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload)).setMimeType(ContentService.MimeType.JSON);
}

function setup() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  ss.rename("BelayaLiniya — Leads");
  ss.setSpreadsheetTimeZone("Europe/Moscow");

  var leads = ss.getSheetByName("leads") || ss.insertSheet("leads");
  var headers = ["request_id", "created_at", "name", "phone", "email", "service", "preferred_time", "utm_source", "utm_medium", "utm_campaign", "utm_content", "status"];
  leads.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight("bold");
  leads.setFrozenRows(1);
  leads.getRange("D:D").setNumberFormat("@");

  var serviceRule = SpreadsheetApp.newDataValidation().requireValueInList(SERVICES, true).build();
  var timeRule = SpreadsheetApp.newDataValidation().requireValueInList(TIMES, true).build();
  var statusRule = SpreadsheetApp.newDataValidation().requireValueInList(["new", "contacted", "appointment", "visited", "lost"], true).build();
  leads.getRange("F2:F").setDataValidation(serviceRule);
  leads.getRange("G2:G").setDataValidation(timeRule);
  leads.getRange("L2:L").setDataValidation(statusRule);

  leads.clearConditionalFormatRules();
  var required = ["A2:D500", "F2:L500"];
  var rules = required.map(function (range) {
    return SpreadsheetApp.newConditionalFormatRule().whenCellEmpty().setBackground("#F4C7C3").setRanges([leads.getRange(range)]).build();
  });
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied('=AND(A2<>"",COUNTIF($A$2:$A,A2)>1)')
    .setBackground("#F6D58A")
    .setRanges([leads.getRange("A2:A500")])
    .build());
  leads.setConditionalFormatRules(rules);

  var dict = ss.getSheetByName("dict") || ss.insertSheet("dict");
  dict.clear();
  dict.getRange(1, 1, 1, 2).setValues([["service", "label"]]);
  var serviceRows = SERVICES.map(function (code) { return [code, SERVICE_LABELS[code]]; });
  dict.getRange(2, 1, serviceRows.length, 2).setValues(serviceRows);
  dict.getRange(1, 4, 1, 2).setValues([["status", "stage"]]);
  var stages = Object.keys(STAGE_LABELS).map(function (code) { return [code, STAGE_LABELS[code]]; });
  dict.getRange(2, 4, stages.length, 2).setValues(stages);

  var crm = ss.getSheetByName("crm_import") || ss.insertSheet("crm_import");
  crm.clear();
  var crmHeaders = ["request_id", "created_at", "first_name", "last_name", "phone", "email", "service", "preferred_time", "utm_source", "utm_medium", "utm_campaign", "utm_content", "deal_stage", "deal_name"];
  crm.getRange(1, 1, 1, crmHeaders.length).setValues([crmHeaders]).setFontWeight("bold");
  crm.getRange("A2").setFormula('=ARRAYFORMULA(IF(leads!A2:A="","",leads!A2:A))');
  crm.getRange("B2").setFormula('=ARRAYFORMULA(IF(leads!A2:A="","",leads!B2:B))');
  crm.getRange("C2").setFormula('=ARRAYFORMULA(IF(leads!C2:C="","",IFERROR(REGEXEXTRACT(TRIM(leads!C2:C),"^[^ ]+"),TRIM(leads!C2:C))))');
  crm.getRange("D2").setFormula('=ARRAYFORMULA(IF(leads!C2:C="","",IFERROR(REGEXEXTRACT(TRIM(leads!C2:C),"^[^ ]+ (.*)$"),"")))');
  crm.getRange("E2").setFormula('=ARRAYFORMULA(IF(leads!D2:D="","",IF(REGEXMATCH(REGEXREPLACE(leads!D2:D,"\\D",""),"^7\\d{10}$"),"+"&REGEXREPLACE(leads!D2:D,"\\D",""),IF(REGEXMATCH(REGEXREPLACE(leads!D2:D,"\\D",""),"^8\\d{10}$"),"+7"&RIGHT(REGEXREPLACE(leads!D2:D,"\\D",""),10),leads!D2:D))))');
  crm.getRange("F2").setFormula('=ARRAYFORMULA(IF(leads!A2:A="","",leads!E2:E))');
  crm.getRange("G2").setFormula('=ARRAYFORMULA(IF(leads!A2:A="","",leads!F2:F))');
  crm.getRange("H2").setFormula('=ARRAYFORMULA(IF(leads!A2:A="","",leads!G2:G))');
  crm.getRange("I2").setFormula('=ARRAYFORMULA(IF(leads!A2:A="","",leads!H2:H))');
  crm.getRange("J2").setFormula('=ARRAYFORMULA(IF(leads!A2:A="","",leads!I2:I))');
  crm.getRange("K2").setFormula('=ARRAYFORMULA(IF(leads!A2:A="","",leads!J2:J))');
  crm.getRange("L2").setFormula('=ARRAYFORMULA(IF(leads!A2:A="","",leads!K2:K))');
  crm.getRange("M2").setFormula('=ARRAYFORMULA(IF(leads!L2:L="","",IFERROR(VLOOKUP(leads!L2:L,dict!D2:E,2,FALSE),leads!L2:L)))');
  crm.getRange("N2").setFormula('=ARRAYFORMULA(IF(leads!A2:A="","",leads!C2:C&" — "&IFERROR(VLOOKUP(leads!F2:F,dict!A2:B,2,FALSE),leads!F2:F)&" — "&TEXT(leads!B2:B,"dd.mm.yyyy")))');

  var defaultSheet = ss.getSheetByName("Sheet1") || ss.getSheetByName("Лист1");
  if (defaultSheet && defaultSheet.getLastRow() === 0) ss.deleteSheet(defaultSheet);
}
