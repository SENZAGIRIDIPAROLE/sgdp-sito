/* SGDP – script del sito
   Unica cosa da configurare: l'indirizzo della pubblicazione Substack. */
var SGDP_CONFIG = {
  SUBSTACK_URL: "https://senzagiridiparolesgdp.substack.com" // indirizzo della pubblicazione Substack (senza barra finale)
};

(function () {
  var CHIAVE_SBLOCCO = "sgdp_iscritto";
  var CHIAVE_CONSENSO = "sgdp_consenso_substack";

  function leggi(k) { try { return window.localStorage.getItem(k) === "1"; } catch (e) { return false; } }
  function salva(k) { try { window.localStorage.setItem(k, "1"); } catch (e) { /* solo per questa visita */ } }
  function togli(k) { try { window.localStorage.removeItem(k); } catch (e) { /* niente da togliere */ } }

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

  // Modulo ufficiale di Substack: si carica solo dopo il consenso, perché Substack salva un cookie di statistica.
  var base = (SGDP_CONFIG.SUBSTACK_URL || "").replace(/\/+$/, "");
  var consensoInSessione = false;
  function mostraModuli() {
    document.querySelectorAll(".modulo-substack").forEach(function (box) {
      var cornice = box.querySelector(".cornice-substack");
      if (!cornice.querySelector("iframe")) {
        var f = document.createElement("iframe");
        f.src = base + "/embed";
        f.title = "Iscrizione alla newsletter di SGDP";
        f.setAttribute("frameborder", "0");
        f.setAttribute("scrolling", "no");
        cornice.appendChild(f);
      }
      cornice.hidden = false;
      box.querySelector(".consenso-substack").hidden = true;
    });
  }
  document.querySelectorAll("[data-mostra-substack]").forEach(function (b) {
    b.addEventListener("click", function () { consensoInSessione = true; salva(CHIAVE_CONSENSO); mostraModuli(); });
  });
  if (base && (leggi(CHIAVE_CONSENSO) || consensoInSessione)) mostraModuli();

  // Dopo l'iscrizione il lettore sblocca l'articolo con un clic.
  document.querySelectorAll("[data-sblocca]").forEach(function (b) {
    b.addEventListener("click", function () { salva(CHIAVE_SBLOCCO); sblocca(); });
  });
  if (leggi(CHIAVE_SBLOCCO)) sblocca();

  // Pagina cookie: revoca del consenso.
  var revoca = document.querySelector("[data-revoca]");
  if (revoca) {
    revoca.addEventListener("click", function () {
      togli(CHIAVE_CONSENSO);
      var esito = document.getElementById("esito-revoca");
      if (esito) esito.textContent = "Consenso revocato: il modulo di Substack non verrà più caricato finché non lo accetti di nuovo.";
    });
  }

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
