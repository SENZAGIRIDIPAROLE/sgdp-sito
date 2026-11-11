/* SGDP – script del sito
   Unica cosa da configurare: l'indirizzo della pubblicazione Substack. */
var SGDP_CONFIG = {
  SUBSTACK_URL: "https://senzagiridiparolesgdp.substack.com" // indirizzo della pubblicazione Substack (senza barra finale)
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

  var formatoEmail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  // Un solo clic, senza uscire dal sito: l'email viene inviata a Substack in sottofondo.
  // Se lo script non funziona, il modulo apre la pagina di iscrizione di Substack (riserva).
  document.querySelectorAll("form.modulo:not(.modulo-gia)").forEach(function (form) {
    var errore = form.querySelector(".errore");
    var passo2 = form.querySelector(".passo2");
    var istruzioni = form.querySelector(".istruzioni");
    var avvisoConfig = form.querySelector(".avviso-config");
    var bottone = form.querySelector("button[type=submit]");
    var testoBottone = bottone.textContent;
    var base = (SGDP_CONFIG.SUBSTACK_URL || "").replace(/\/+$/, "");

    function mostraEsito(configurato) {
      if (istruzioni) istruzioni.hidden = !configurato;
      if (avvisoConfig) avvisoConfig.hidden = configurato;
      passo2.hidden = false;
      form.querySelector(".riga-campo").hidden = true;
      salva();
      sblocca();
      var ea = document.querySelector(".esito-articolo");
      if (ea && configurato) ea.hidden = false;
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var email = (form.querySelector("input[type=email]").value || "").trim();
      if (!formatoEmail.test(email)) {
        errore.textContent = "Scrivi un indirizzo email valido, per esempio nome@esempio.it.";
        errore.hidden = false;
        return;
      }
      errore.hidden = true;
      if (!base) { mostraEsito(false); return; }
      bottone.disabled = true;
      bottone.textContent = "Invio…";
      var dati = "email=" + encodeURIComponent(email) + "&source=embed&first_url=" + encodeURIComponent(location.href);
      fetch(base + "/api/v1/free?nojs=true", {
        method: "POST",
        mode: "no-cors",
        credentials: "omit",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: dati
      }).then(function () {
        mostraEsito(true);
      }).catch(function () {
        // Rete o blocco: si ripiega sulla pagina di iscrizione di Substack.
        bottone.disabled = false;
        bottone.textContent = testoBottone;
        errore.innerHTML = "Non siamo riusciti a completare l'iscrizione da qui. <a href=\"" + base + "/subscribe?email=" + encodeURIComponent(email) + "\" target=\"_blank\" rel=\"noopener\">Iscriviti su Substack</a>.";
        errore.hidden = false;
      });
    });
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
