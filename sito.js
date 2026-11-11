/* SGDP – script del sito
   Unica cosa da configurare: l'indirizzo della pubblicazione Substack. */
var SGDP_CONFIG = {
  SUBSTACK_URL: "" // esempio: "https://sgdp.substack.com" (senza barra finale)
};

(function () {
  var CHIAVE = "sgdp_iscritto";

  function leggi() {
    try { return window.localStorage.getItem(CHIAVE) === "1"; } catch (e) { return false; }
  }
  function salva() {
    try { window.localStorage.setItem(CHIAVE, "1"); } catch (e) { /* archiviazione non disponibile: lo sblocco vale solo per questa visita */ }
  }

  function sblocca() {
    var corpo = document.querySelector(".corpo.bloccato");
    if (corpo) {
      corpo.classList.remove("bloccato");
      corpo.removeAttribute("inert");
      corpo.removeAttribute("aria-hidden");
    }
    var muro = document.querySelector(".muro");
    if (muro) muro.hidden = true;
  }

  function indirizzoSubstack(email) {
    var base = (SGDP_CONFIG.SUBSTACK_URL || "").replace(/\/+$/, "");
    if (!base) return "";
    return base + "/subscribe?email=" + encodeURIComponent(email);
  }

  var formatoEmail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  document.querySelectorAll("form.modulo:not(.modulo-gia)").forEach(function (form) {
    var errore = form.querySelector(".errore");
    var passo2 = form.querySelector(".passo2");
    var vai = form.querySelector(".vai-substack");
    var avvisoConfig = form.querySelector(".avviso-config");

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var email = (form.querySelector("input[type=email]").value || "").trim();
      var consensi = form.querySelectorAll("input[type=checkbox][required]");
      var mancano = [];
      if (!formatoEmail.test(email)) mancano.push("un indirizzo email valido");
      consensi.forEach(function (c) { if (!c.checked) mancano.push(c.getAttribute("data-nome")); });
      if (mancano.length) {
        errore.textContent = "Per iscriverti manca: " + mancano.join(", ") + ".";
        errore.hidden = false;
        return;
      }
      errore.hidden = true;
      var url = indirizzoSubstack(email);
      if (url) {
        vai.href = url;
        vai.hidden = false;
        if (avvisoConfig) avvisoConfig.hidden = true;
      } else {
        vai.hidden = true;
        if (avvisoConfig) avvisoConfig.hidden = false;
      }
      passo2.hidden = false;
      form.querySelector(".riga-campo").hidden = true;
      form.querySelectorAll(".consenso").forEach(function (c) { c.hidden = true; });
      if (!url) { salva(); sblocca(); }
    });

    if (vai) {
      vai.addEventListener("click", function () { salva(); sblocca(); });
    }
  });

  var gia = document.querySelector(".gia button");
  if (gia) {
    gia.addEventListener("click", function () {
      var box = document.getElementById("gia-iscritto");
      box.hidden = !box.hidden;
      if (!box.hidden) box.querySelector("input").focus();
    });
  }
  var giaForm = document.getElementById("gia-iscritto");
  if (giaForm) {
    giaForm.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var email = (giaForm.querySelector("input").value || "").trim();
      var err = giaForm.querySelector(".errore");
      if (!formatoEmail.test(email)) { err.textContent = "Inserisci l'email con cui ti sei iscritto."; err.hidden = false; return; }
      salva();
      sblocca();
    });
  }

  if (leggi()) sblocca();

  var copia = document.querySelector("[data-copia]");
  if (copia) {
    copia.addEventListener("click", function () {
      var testo = document.getElementById(copia.getAttribute("data-copia")).textContent;
      var esito = document.getElementById("esito-copia");
      function selezione() {
        var r = document.createRange();
        r.selectNodeContents(document.getElementById(copia.getAttribute("data-copia")));
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        esito.textContent = "Indirizzo selezionato: copialo con Ctrl+C o tieni premuto.";
      }
      try {
        navigator.clipboard.writeText(testo).then(function () { esito.textContent = "Indirizzo copiato."; }, selezione);
      } catch (e) { selezione(); }
    });
  }
})();
