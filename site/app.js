(function () {
  "use strict";

  const state = {
    country: "es",
    records: [],
    search: null,
    metadata: null,
    authority: "AEMPS",
  };

  const els = {
    status: document.getElementById("datasetStatus"),
    input: document.getElementById("searchInput"),
    countries: document.getElementById("countryButtons"),
    dateFrom: document.getElementById("dateFrom"),
    dateTo: document.getElementById("dateTo"),
    sortMode: document.getElementById("sortMode"),
    manufacturer: document.getElementById("manufacturerFilter"),
    recallClass: document.getElementById("classFilter"),
    years: document.getElementById("yearFilters"),
    activeFilters: document.getElementById("activeFilters"),
    clear: document.getElementById("clearButton"),
    exactOnly: document.getElementById("exactOnly"),
    showWarnings: document.getElementById("showWarnings"),
    count: document.getElementById("resultCount"),
    headerLastUpdate: document.getElementById("headerLastUpdate"),
    lastUpdate: document.getElementById("lastUpdate"),
    authority: document.getElementById("sourceAuthority"),
    results: document.getElementById("results"),
    template: document.getElementById("resultTemplate"),
  };

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    bindEvents();
    try {
      state.metadata = await fetchJson("data/metadata.json");
      configureCountries(state.metadata.countries || [], state.metadata.default_country);
      await loadCountry(state.country);
    } catch (error) {
      showError("No se pudieron cargar los datos estáticos.");
      els.status.textContent = "Datos no disponibles";
    }
  }

  function bindEvents() {
    els.input.addEventListener("input", render);
    els.dateFrom.addEventListener("change", render);
    els.dateTo.addEventListener("change", render);
    els.sortMode.addEventListener("change", render);
    els.manufacturer.addEventListener("change", render);
    els.recallClass.addEventListener("change", render);
    els.activeFilters.addEventListener("click", onActiveFilterClick);
    els.countries.addEventListener("keydown", onCountryKeydown);
    els.clear.addEventListener("click", function () {
      els.input.value = "";
      els.dateFrom.value = "";
      els.dateTo.value = "";
      els.manufacturer.value = "";
      els.recallClass.value = "";
      clearYearButtons();
      els.input.focus();
      render();
    });
    els.exactOnly.addEventListener("change", render);
    els.showWarnings.addEventListener("change", render);
  }

  async function onCountryKeydown(event) {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
      return;
    }
    const buttons = Array.from(els.countries.querySelectorAll(".country-button:not(:disabled)"));
    if (!buttons.length) {
      return;
    }
    event.preventDefault();
    const current = Math.max(0, buttons.findIndex(function (button) {
      return button.dataset.country === state.country;
    }));
    let next = current;
    if (event.key === "ArrowLeft") {
      next = current === 0 ? buttons.length - 1 : current - 1;
    } else if (event.key === "ArrowRight") {
      next = current === buttons.length - 1 ? 0 : current + 1;
    } else if (event.key === "Home") {
      next = 0;
    } else if (event.key === "End") {
      next = buttons.length - 1;
    }
    buttons[next].focus();
    await loadCountry(buttons[next].dataset.country);
  }

  function configureCountries(countries, defaultCountry) {
    els.countries.innerHTML = "";
    countries.forEach(function (country) {
      const disabled = country.status === "planned" || Number(country.records || 0) === 0;
      const button = document.createElement("button");
      button.type = "button";
      button.className = disabled ? "country-button country-button--disabled" : "country-button";
      button.dataset.country = country.code;
      button.setAttribute("role", "tab");
      button.setAttribute("aria-label", formatCountryOption(country));
      button.disabled = disabled;
      button.title = disabled
        ? `${formatCountryOption(country)}: fuente planificada, todavía sin datos activos.`
        : `${formatCountryOption(country)}: cambiar a este conjunto de datos.`;
      button.innerHTML = [
        `<span class="country-button__flag" aria-hidden="true">${country.flag || country.iso2 || country.code.toUpperCase()}</span>`,
        `<span class="country-button__label">${country.iso2 || country.code.toUpperCase()}</span>`,
        disabled ? '<span class="country-button__status">Próx.</span>' : "",
      ].join("");
      button.addEventListener("click", async function () {
        if (!disabled) {
          await loadCountry(country.code);
        }
      });
      els.countries.appendChild(button);
    });
    const activeCountries = countries.filter(function (country) {
      return country.status !== "planned" && Number(country.records || 0) > 0;
    });
    state.country = activeCountries.some(function (country) { return country.code === defaultCountry; })
      ? defaultCountry
      : (activeCountries[0] ? activeCountries[0].code : "es");
    updateCountryButtons();
  }

  function formatCountryOption(country) {
    const flag = country.flag ? `${country.flag} ` : "";
    const name = country.name || country.iso2 || country.code.toUpperCase();
    const authority = country.authority ? ` - ${country.authority}` : "";
    return `${flag}${name}${authority}`;
  }

  async function loadCountry(country) {
    state.country = country;
    const [countryMetadata, records] = await Promise.all([
      fetchJson(`data/countries/${country}/metadata.json`),
      fetchJson(`data/countries/${country}/recalls-summary.json`),
    ]);
    state.records = records;
    state.search = createSearch(records);
    state.authority = countryMetadata.authority || countryMetadata.name || country.toUpperCase();
    renderFacets(records);
    renderYearFilters(records);
    els.headerLastUpdate.textContent = formatDateTime(countryMetadata.generated_at);
    els.lastUpdate.textContent = formatDateTime(countryMetadata.generated_at);
    els.authority.textContent = state.authority;
    els.status.textContent = `${records.length} retiradas indexadas`;
    updateCountryButtons();
    render();
  }

  function updateCountryButtons() {
    els.countries.querySelectorAll(".country-button").forEach(function (button) {
      const active = button.dataset.country === state.country;
      button.setAttribute("aria-selected", active ? "true" : "false");
      button.tabIndex = active ? 0 : -1;
    });
  }

  function renderYearFilters(records) {
    const years = Array.from(new Set(records.map(function (record) {
      return String(record.date || "").slice(0, 4);
    }).filter(Boolean))).sort().reverse();
    els.years.innerHTML = "";
    years.forEach(function (year) {
      const count = records.filter(function (record) {
        return String(record.date || "").startsWith(year);
      }).length;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "year-button";
      button.dataset.year = year;
      button.setAttribute("aria-pressed", "false");
      button.textContent = `${year} (${count})`;
      button.title = `Filtrar resultados publicados en ${year}. ${count} registros.`;
      button.setAttribute("aria-label", button.title);
      button.addEventListener("click", function () {
        const selected = button.getAttribute("aria-pressed") === "true";
        clearYearButtons();
        if (selected) {
          els.dateFrom.value = "";
          els.dateTo.value = "";
        } else {
          button.setAttribute("aria-pressed", "true");
          els.dateFrom.value = `${year}-01-01`;
          els.dateTo.value = `${year}-12-31`;
        }
        render();
      });
      els.years.appendChild(button);
    });
  }

  function renderFacets(records) {
    populateSelect(
      els.manufacturer,
      "Todos los laboratorios",
      countValues(records.map(function (record) { return record.manufacturer || ""; }))
    );
    populateSelect(
      els.recallClass,
      "Todas las clases",
      countValues(records.map(function (record) {
        return record.recall_class ? `Clase ${record.recall_class}` : "";
      }))
    );
  }

  function countValues(values) {
    const counts = new Map();
    values.filter(Boolean).forEach(function (value) {
      counts.set(value, (counts.get(value) || 0) + 1);
    });
    return Array.from(counts.entries()).sort(function (left, right) {
      if (right[1] !== left[1]) {
        return right[1] - left[1];
      }
      return left[0].localeCompare(right[0]);
    });
  }

  function populateSelect(select, label, entries) {
    select.innerHTML = "";
    const all = document.createElement("option");
    all.value = "";
    all.textContent = label;
    select.appendChild(all);
    entries.forEach(function (entry) {
      const option = document.createElement("option");
      option.value = entry[0];
      option.textContent = `${entry[0]} (${entry[1]})`;
      select.appendChild(option);
    });
  }

  function clearYearButtons() {
    els.years.querySelectorAll(".year-button").forEach(function (button) {
      button.setAttribute("aria-pressed", "false");
    });
  }

  function createSearch(records) {
    if (!window.MiniSearch) {
      return null;
    }
    const search = new window.MiniSearch({
      fields: ["medicine", "manufacturer", "reason"],
      storeFields: ["id"],
      searchOptions: {
        boost: { medicine: 3, manufacturer: 2 },
        fuzzy: 0.2,
        prefix: true,
      },
    });
    search.addAll(records.map(function (record) {
      return {
        id: record.id,
        medicine: record.medicine || "",
        manufacturer: record.manufacturer || "",
        reason: record.reason || "",
      };
    }));
    return search;
  }

  function render() {
    const query = els.input.value.trim();
    const results = filteredResults(query);
    els.count.textContent = String(results.length);
    renderActiveFilters(query);
    els.results.innerHTML = "";
    if (!results.length) {
      const empty = document.createElement("p");
      empty.className = "empty";
      empty.textContent = `No se encontró ninguna retirada coincidente en los registros indexados de ${state.authority}.`;
      els.results.appendChild(empty);
      return;
    }
    results.slice(0, 100).forEach(function (result) {
      els.results.appendChild(renderRecord(result.record, result.match));
    });
  }

  function renderActiveFilters(query) {
    const filters = activeFilters(query);
    els.activeFilters.innerHTML = "";
    if (!filters.length) {
      return;
    }
    filters.forEach(function (filter) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "filter-chip";
      button.dataset.filter = filter.key;
      button.innerHTML = `<span>${filter.label}</span><strong aria-hidden="true">×</strong>`;
      button.setAttribute("aria-label", `Quitar filtro ${filter.label}`);
      button.title = `Quitar filtro ${filter.label}`;
      els.activeFilters.appendChild(button);
    });
    const clear = document.createElement("button");
    clear.type = "button";
    clear.className = "filter-chip filter-chip--clear";
    clear.dataset.filter = "all";
    clear.textContent = "Limpiar todo";
    clear.title = "Quitar todos los filtros activos";
    clear.setAttribute("aria-label", clear.title);
    els.activeFilters.appendChild(clear);
  }

  function activeFilters(query) {
    const filters = [];
    if (query) {
      filters.push({ key: "query", label: `Texto: ${query}` });
    }
    if (els.dateFrom.value) {
      filters.push({ key: "dateFrom", label: `Desde: ${formatDate(els.dateFrom.value)}` });
    }
    if (els.dateTo.value) {
      filters.push({ key: "dateTo", label: `Hasta: ${formatDate(els.dateTo.value)}` });
    }
    if (els.manufacturer.value) {
      filters.push({ key: "manufacturer", label: `Lab: ${els.manufacturer.value}` });
    }
    if (els.recallClass.value) {
      filters.push({ key: "class", label: els.recallClass.value });
    }
    if (els.exactOnly.checked) {
      filters.push({ key: "exact", label: "Exactas" });
    }
    return filters;
  }

  function onActiveFilterClick(event) {
    const button = event.target.closest(".filter-chip");
    if (!button) {
      return;
    }
    removeFilter(button.dataset.filter);
    render();
  }

  function removeFilter(filter) {
    if (filter === "all") {
      els.input.value = "";
      els.dateFrom.value = "";
      els.dateTo.value = "";
      els.manufacturer.value = "";
      els.recallClass.value = "";
      els.exactOnly.checked = false;
      clearYearButtons();
      return;
    }
    if (filter === "query") {
      els.input.value = "";
    } else if (filter === "dateFrom") {
      els.dateFrom.value = "";
      clearYearButtons();
    } else if (filter === "dateTo") {
      els.dateTo.value = "";
      clearYearButtons();
    } else if (filter === "manufacturer") {
      els.manufacturer.value = "";
    } else if (filter === "class") {
      els.recallClass.value = "";
    } else if (filter === "exact") {
      els.exactOnly.checked = false;
    }
  }

  function filteredResults(query) {
    const base = query ? searchRecords(query) : state.records.map(withBrowseMatch);
    return sortResults(base.filter(function (result) {
      return recordInDateRange(result.record) && recordMatchesFacets(result.record);
    }));
  }

  function recordInDateRange(record) {
    const date = record.date || "";
    if (els.dateFrom.value && date < els.dateFrom.value) {
      return false;
    }
    if (els.dateTo.value && date > els.dateTo.value) {
      return false;
    }
    return true;
  }

  function recordMatchesFacets(record) {
    if (els.manufacturer.value && record.manufacturer !== els.manufacturer.value) {
      return false;
    }
    if (els.recallClass.value) {
      return `Clase ${record.recall_class || ""}` === els.recallClass.value;
    }
    return true;
  }

  function sortResults(results) {
    const direction = els.sortMode.value === "oldest" ? 1 : -1;
    return results.slice().sort(function (left, right) {
      const byDate = String(left.record.date || "").localeCompare(String(right.record.date || ""));
      if (byDate !== 0) {
        return byDate * direction;
      }
      return String(left.record.id || "").localeCompare(String(right.record.id || "")) * direction;
    });
  }

  function searchRecords(query) {
    const exact = exactMatches(query);
    if (els.exactOnly.checked) {
      return exact;
    }

    const seen = new Set(exact.map(function (item) { return item.record.id; }));
    const fuzzy = fuzzyMatches(query)
      .filter(function (item) { return !seen.has(item.record.id); });
    return exact.concat(fuzzy);
  }

  function exactMatches(query) {
    const normalized = normalize(query);
    const digits = query.replace(/\D/g, "");
    const local = normalized.replace(/\//g, "_");
    const matches = [];
    state.records.forEach(function (record) {
      const codes = record.product_codes || [];
      if (codes.some(function (code) { return code.value === digits && digits.length > 0; })) {
        matches.push(withMatch(record, "código exacto"));
        return;
      }
      if (record.date === query) {
        matches.push(withMatch(record, "fecha exacta"));
        return;
      }
      if (record.date && record.date.startsWith(query) && /^\d{4}(-\d{2})?$/.test(query)) {
        matches.push(withMatch(record, "fecha"));
        return;
      }
      if ((record.lots || []).some(function (lot) { return normalize(lot) === normalized; })) {
        matches.push(withMatch(record, "lote exacto"));
        return;
      }
      if (normalize(record.local_id || "").replace(/\//g, "_") === local || normalize(record.id || "") === local) {
        matches.push(withMatch(record, "alerta exacta"));
      }
    });
    return matches;
  }

  function fuzzyMatches(query) {
    if (state.search) {
      return state.search.search(query).map(function (hit) {
        return withMatch(findRecord(hit.id), "texto similar");
      }).filter(function (item) {
        return Boolean(item.record);
      });
    }
    const normalized = normalize(query);
    return state.records.filter(function (record) {
      return normalize([record.medicine, record.manufacturer, record.reason].join(" ")).includes(normalized);
    }).map(function (record) {
      return withMatch(record, "texto similar");
    });
  }

  function renderRecord(record, match) {
    const fragment = els.template.content.cloneNode(true);
    const card = fragment.querySelector(".result-card");
    card.dataset.class = record.recall_class || "unknown";
    const alertChip = fragment.querySelector('[data-field="alert"]');
    alertChip.textContent = record.local_id || record.id;
    setTooltip(alertChip, "Identificador de la alerta o circular publicado por la fuente.");

    const dateChip = fragment.querySelector('[data-field="date"]');
    dateChip.textContent = formatDate(record.date);
    setTooltip(dateChip, "Fecha normalizada usada para ordenar y filtrar este registro.");

    const matchChip = fragment.querySelector('[data-field="match"]');
    matchChip.textContent = match;
    setTooltip(matchChip, matchExplanation(match));
    fragment.querySelector("h2").textContent = record.medicine || record.local_id;
    fragment.querySelector('[data-field="manufacturer"]').textContent = record.manufacturer || "Laboratorio no extraído";
    const classBadge = fragment.querySelector('[data-field="class"]');
    classBadge.textContent = record.recall_class ? `Clase ${record.recall_class}` : "Sin clase publicada";
    setTooltip(classBadge, recallClassExplanation(record.recall_class));

    const parseBadge = fragment.querySelector('[data-field="parse"]');
    parseBadge.textContent = parseStatus(record);
    setTooltip(parseBadge, parseStatusExplanation(record));
    fragment.querySelector('[data-field="codes"]').textContent = formatCodes(record.product_codes);
    fragment.querySelector('[data-field="lots"]').textContent = (record.lots || []).join(", ") || "-";
    fragment.querySelector('[data-field="reason"]').textContent = record.reason || "-";
    fragment.querySelector('[data-field="confidence"]').textContent = `${Math.round((record.confidence || 0) * 100)}%`;

    renderWarnings(fragment.querySelector(".warnings"), record);

    const source = fragment.querySelector('[data-field="source"]');
    source.href = record.source_url;
    source.title = `Abrir fuente oficial de ${record.authority || state.authority}.`;
    source.setAttribute("aria-label", source.title);
    const pdf = fragment.querySelector('[data-field="pdf"]');
    if (record.pdf_url) {
      pdf.href = record.pdf_url;
      pdf.title = "Abrir PDF oficial asociado a este registro.";
      pdf.setAttribute("aria-label", pdf.title);
    } else {
      pdf.remove();
    }
    return fragment;
  }

  function parseStatus(record) {
    const warnings = record.warnings || [];
    if (!warnings.length) {
      return "Completo";
    }
    if (warnings.some(function (warning) { return warning.startsWith("missing_"); })) {
      return "Revisar";
    }
    return "Extraído";
  }

  function parseStatusExplanation(record) {
    const warnings = record.warnings || [];
    if (!warnings.length) {
      return "Completo: los campos estructurados esperados se extrajeron sin avisos.";
    }
    if (warnings.some(function (warning) { return warning.startsWith("missing_"); })) {
      return "Revisar: faltan uno o más campos estructurados. Usa la fuente oficial para confirmar.";
    }
    return "Extraído: el registro fue procesado, pero el parser generó avisos informativos.";
  }

  function recallClassExplanation(recallClass) {
    const explanations = {
      1: "Clase 1: defecto con riesgo potencialmente grave. Acento rojo.",
      2: "Clase 2: defecto con riesgo relevante pero menor que clase 1. Acento ámbar.",
      3: "Clase 3: defecto con menor probabilidad de riesgo clínico. Acento verde azulado.",
    };
    return explanations[recallClass] || "La fuente no publica una clase de retirada normalizada. Acento gris.";
  }

  function matchExplanation(match) {
    const explanations = {
      reciente: "Resultado mostrado por exploración inicial, sin término de búsqueda activo.",
      "texto similar": "Coincidencia por búsqueda difusa en medicamento, laboratorio o motivo.",
      "código exacto": "Coincidencia exacta con un código de producto.",
      "fecha exacta": "Coincidencia exacta con la fecha normalizada del registro.",
      fecha: "Coincidencia con año o mes de la fecha normalizada.",
      "lote exacto": "Coincidencia exacta con un lote extraído.",
      "alerta exacta": "Coincidencia exacta con el identificador local o global de la alerta.",
    };
    return explanations[match] || `Tipo de coincidencia: ${match}.`;
  }

  function setTooltip(element, text) {
    element.title = text;
    element.setAttribute("aria-label", text);
  }

  function renderWarnings(container, record) {
    container.replaceChildren();
    if (!els.showWarnings.checked || !record.warnings || !record.warnings.length) {
      return;
    }

    const label = document.createElement("span");
    label.className = "warnings__label";
    label.textContent = "Avisos de extracción";
    label.title = "Campos que no pudieron extraerse de forma estructurada desde la fuente.";
    container.appendChild(label);

    record.warnings.forEach(function (warning) {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "warning-chip";
      chip.textContent = warningLabel(warning);
      chip.title = warningExplanation(warning);
      chip.setAttribute("aria-label", `${warningLabel(warning)}: ${warningExplanation(warning)}`);
      container.appendChild(chip);
    });
  }

  function warningLabel(warning) {
    const labels = {
      missing_cn: "Sin CN",
      missing_cip: "Sin CIP",
      missing_registration_number: "Sin registro",
      missing_lot: "Sin lote",
      missing_manufacturer: "Sin laboratorio",
    };
    return labels[warning] || warning.replace(/_/g, " ");
  }

  function warningExplanation(warning) {
    const explanations = {
      missing_cn: "No se encontró Código Nacional en la fuente española. El registro sigue indexado; verifica la fuente oficial para identificación por código.",
      missing_cip: "No se encontró código CIP en la fuente francesa. El registro sigue indexado; no será localizable por CIP salvo enriquecimiento posterior.",
      missing_registration_number: "No se encontró número de registro/AIM en la fuente portuguesa. El registro sigue indexado; verifica la fuente oficial para identificación por código.",
      missing_lot: "No se pudo extraer un lote estructurado. El aviso puede seguir siendo válido; revisa la fuente oficial antes de actuar.",
      missing_manufacturer: "No se pudo extraer el laboratorio o titular. Revisa la fuente oficial para confirmar el responsable.",
    };
    return explanations[warning] || `Aviso del parser: ${warning}. Revisa la fuente oficial.`;
  }

  function withMatch(record, match) {
    return { record, match };
  }

  function withBrowseMatch(record) {
    return withMatch(record, "reciente");
  }

  function findRecord(id) {
    return state.records.find(function (record) { return record.id === id; });
  }

  function formatCodes(codes) {
    if (!codes || !codes.length) {
      return "-";
    }
    return codes.map(function (code) { return `${code.system}: ${code.value}`; }).join(", ");
  }

  function normalize(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim()
      .toUpperCase();
  }

  function formatDate(value) {
    if (!value) {
      return "-";
    }
    return new Intl.DateTimeFormat("es-ES", { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`));
  }

  function formatDateTime(value) {
    if (!value) {
      return "-";
    }
    return new Intl.DateTimeFormat("es-ES", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
  }

  async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} for ${url}`);
    }
    return response.json();
  }

  function showError(message) {
    els.results.innerHTML = "";
    const error = document.createElement("p");
    error.className = "error";
    error.textContent = message;
    els.results.appendChild(error);
  }
})();
