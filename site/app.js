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
    country: document.getElementById("countrySelect"),
    input: document.getElementById("searchInput"),
    clear: document.getElementById("clearButton"),
    exactOnly: document.getElementById("exactOnly"),
    showWarnings: document.getElementById("showWarnings"),
    count: document.getElementById("resultCount"),
    lastUpdate: document.getElementById("lastUpdate"),
    results: document.getElementById("results"),
    template: document.getElementById("resultTemplate"),
  };

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    bindEvents();
    try {
      state.metadata = await fetchJson("data/metadata.json");
      configureCountries(state.metadata.countries || []);
      await loadCountry(state.country);
    } catch (error) {
      showError("No se pudieron cargar los datos estáticos.");
      els.status.textContent = "Datos no disponibles";
    }
  }

  function bindEvents() {
    els.input.addEventListener("input", render);
    els.clear.addEventListener("click", function () {
      els.input.value = "";
      els.input.focus();
      render();
    });
    els.exactOnly.addEventListener("change", render);
    els.showWarnings.addEventListener("change", render);
    els.country.addEventListener("change", async function () {
      await loadCountry(els.country.value);
    });
  }

  function configureCountries(countries) {
    els.country.innerHTML = "";
    countries.forEach(function (country) {
      const option = document.createElement("option");
      option.value = country.code;
      option.textContent = country.code === "es" ? "España - AEMPS" : country.code.toUpperCase();
      els.country.appendChild(option);
    });
    els.country.disabled = countries.length < 2;
    state.country = countries[0] ? countries[0].code : "es";
  }

  async function loadCountry(country) {
    state.country = country;
    const [countryMetadata, records] = await Promise.all([
      fetchJson(`data/countries/${country}/metadata.json`),
      fetchJson(`data/countries/${country}/recalls-summary.json`),
    ]);
    state.records = records;
    state.search = createSearch(records);
    els.lastUpdate.textContent = formatDateTime(countryMetadata.generated_at);
    els.status.textContent = `${records.length} retiradas indexadas`;
    render();
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
    const results = query ? searchRecords(query) : state.records.slice(0, 25).map(withBrowseMatch);
    els.count.textContent = String(results.length);
    els.results.innerHTML = "";
    if (!results.length) {
      const empty = document.createElement("p");
      empty.className = "empty";
      empty.textContent = "No se encontró ninguna retirada coincidente en los registros indexados de la AEMPS.";
      els.results.appendChild(empty);
      return;
    }
    results.slice(0, 50).forEach(function (result) {
      els.results.appendChild(renderRecord(result.record, result.match));
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
