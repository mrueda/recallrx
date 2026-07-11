(function () {
  "use strict";

  const state = {
    country: "es",
    records: [],
    search: null,
    metadata: null,
  };

  const els = {
    status: document.getElementById("datasetStatus"),
    input: document.getElementById("searchInput"),
    countries: document.getElementById("countryButtons"),
    dateFrom: document.getElementById("dateFrom"),
    dateTo: document.getElementById("dateTo"),
    sortMode: document.getElementById("sortMode"),
    years: document.getElementById("yearFilters"),
    clear: document.getElementById("clearButton"),
    exactOnly: document.getElementById("exactOnly"),
    showWarnings: document.getElementById("showWarnings"),
    count: document.getElementById("resultCount"),
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
    els.countries.addEventListener("keydown", onCountryKeydown);
    els.clear.addEventListener("click", function () {
      els.input.value = "";
      els.dateFrom.value = "";
      els.dateTo.value = "";
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
    const buttons = Array.from(els.countries.querySelectorAll(".country-button"));
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
      const button = document.createElement("button");
      button.type = "button";
      button.className = "country-button";
      button.dataset.country = country.code;
      button.setAttribute("role", "tab");
      button.setAttribute("aria-label", formatCountryOption(country));
      button.innerHTML = [
        `<span class="country-button__flag" aria-hidden="true">${country.flag || country.iso2 || country.code.toUpperCase()}</span>`,
        `<span class="country-button__label">${country.iso2 || country.code.toUpperCase()}</span>`,
      ].join("");
      button.addEventListener("click", async function () {
        await loadCountry(country.code);
      });
      els.countries.appendChild(button);
    });
    state.country = defaultCountry || (countries[0] ? countries[0].code : "es");
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
    renderYearFilters(records);
    els.lastUpdate.textContent = formatDateTime(countryMetadata.generated_at);
    els.authority.textContent = countryMetadata.authority || countryMetadata.name || country.toUpperCase();
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
    els.results.innerHTML = "";
    if (!results.length) {
      const empty = document.createElement("p");
      empty.className = "empty";
      empty.textContent = "No se encontró ninguna retirada coincidente en los registros indexados de la AEMPS.";
      els.results.appendChild(empty);
      return;
    }
    results.slice(0, 100).forEach(function (result) {
      els.results.appendChild(renderRecord(result.record, result.match));
    });
  }

  function filteredResults(query) {
    const base = query ? searchRecords(query) : state.records.map(withBrowseMatch);
    return sortResults(base.filter(function (result) {
      return recordInDateRange(result.record);
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
        matches.push(withMatch(record, "CN exacto"));
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
    fragment.querySelector("h2").textContent = record.medicine || record.local_id;
    fragment.querySelector(".meta").textContent = [
      record.local_id,
      formatDate(record.date),
      record.recall_class ? `Clase ${record.recall_class}` : null,
      match,
    ].filter(Boolean).join(" · ");
    fragment.querySelector(".confidence").textContent = `${Math.round((record.confidence || 0) * 100)}%`;
    fragment.querySelector('[data-field="codes"]').textContent = formatCodes(record.product_codes);
    fragment.querySelector('[data-field="lots"]').textContent = (record.lots || []).join(", ") || "-";
    fragment.querySelector('[data-field="manufacturer"]').textContent = record.manufacturer || "-";
    fragment.querySelector('[data-field="reason"]').textContent = record.reason || "-";

    const warnings = fragment.querySelector(".warnings");
    warnings.textContent = els.showWarnings.checked && record.warnings && record.warnings.length
      ? `Avisos de extracción: ${record.warnings.join(", ")}`
      : "";

    fragment.querySelector('[data-field="source"]').href = record.source_url;
    const pdf = fragment.querySelector('[data-field="pdf"]');
    if (record.pdf_url) {
      pdf.href = record.pdf_url;
    } else {
      pdf.remove();
    }
    return fragment;
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
