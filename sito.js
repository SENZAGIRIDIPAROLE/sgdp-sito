/* SGDP – script del sito
   Le email vanno direttamente a MailerLite (modulo "Sito SGDP", gruppo "Iscritti sito"). */
var SGDP_CONFIG = {
  ISCRIZIONE_URL: "https://assets.mailerlite.com/jsonp/2787607/forms/203851020340561521/subscribe"
};

(function () {
  var CHIAVE_SBLOCCO = "sgdp_iscritto";

  function leggi(k) { try { return window.localStorage.getItem(k) === "1"; } catch (e) { return false; } }
  function salva(k) { try { window.localStorage.setItem(k, "1"); } catch (e) { /* solo per questa visita */ } }

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

  // Iscrizione: email + clic, senza uscire dal sito.
  document.querySelectorAll("[data-modulo]").forEach(function (f) {
    var campo = f.querySelector("input[type=email]");
    var bottone = f.querySelector("button[type=submit]");
    var errore = f.querySelector(".errore");
    var ok = f.querySelector(".passo2");
    f.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var email = (campo.value || "").trim();
      errore.hidden = true;
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
        errore.textContent = "Scrivi un indirizzo email valido.";
        errore.hidden = false; campo.focus(); return;
      }
      bottone.disabled = true;
      var dati = new URLSearchParams();
      dati.append("fields[email]", email);
      dati.append("ml-submit", "1");
      dati.append("anticsrf", "true");
      fetch(SGDP_CONFIG.ISCRIZIONE_URL, { method: "POST", body: dati })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (!j || j.success === false) throw new Error("rifiutata");
          f.querySelector(".riga-campo").hidden = true;
          ok.hidden = false;
          salva(CHIAVE_SBLOCCO);
          if (document.querySelector(".corpo.bloccato")) {
            sblocca();
            var esito = document.querySelector(".esito-articolo");
            if (esito) esito.hidden = false;
          }
        })
        .catch(function () {
          errore.textContent = "Iscrizione non riuscita. Riprova tra poco.";
          errore.hidden = false;
          bottone.disabled = false;
        });
    });
  });

  // Dopo l'iscrizione il lettore sblocca l'articolo con un clic.
  document.querySelectorAll("[data-sblocca]").forEach(function (b) {
    b.addEventListener("click", function () { salva(CHIAVE_SBLOCCO); sblocca(); });
  });
  if (leggi(CHIAVE_SBLOCCO)) sblocca();

  // Pagina contatti: copia dell'indirizzo email.
  var copia = document.querySelector("[data-copia]");
  if (copia) {
    copia.addEventListener("click", function () {
      var el = document.getElementById(copia.getAttribute("data-copia"));
      var esito = document.getElementById("esito-copia");
      function selezione() {
        var r = document.createRange(); r.selectNodeContents(el);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        esito.textContent = "Indirizzo selezionato: copialo con Ctrl+C o tieni premuto.";
      }
      try { navigator.clipboard.writeText(el.textContent).then(function () { esito.textContent = "Indirizzo copiato."; }, selezione); }
      catch (e) { selezione(); }
    });
  }
})();
