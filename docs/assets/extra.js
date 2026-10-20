// Comportements du site de documentation (plugin doc-projet).
// 1. Année du pied de page : calculée à l'affichage, jamais écrite en dur.
// 2. Barre latérale repliable : état retenu d'une visite à l'autre (confort local, facultatif).
// 3. Diagrammes : un clic (ou le bouton « Agrandir ») les ouvre en grand ; Échap ou « Fermer » les referme.
(function () {
  "use strict";

  var ICONES = {
    plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
    moins: '<path d="M5 12h14"/>',
    ajuster: '<path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/>',
    fermer: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>'
  };
  function icone(nom) {
    return '<svg class="lucide" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONES[nom] + "</svg>";
  }

  // --- 1. Année -------------------------------------------------------------------------
  function poserAnnee() {
    document.querySelectorAll(".annee-courante").forEach(function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  // --- 2. Barre latérale ----------------------------------------------------------------
  function lireRepli() {
    try { return localStorage.getItem("facil.nav.repliee") === "1"; } catch (e) { return false; }
  }
  function ecrireRepli(v) {
    try { localStorage.setItem("facil.nav.repliee", v ? "1" : "0"); } catch (e) { /* sans stockage : sans mémoire */ }
  }
  function appliquerRepli(replie) {
    document.documentElement.classList.toggle("facil-nav-repliee", replie);
    document.querySelectorAll(".facil-marque__bascule").forEach(function (b) {
      var libelle = replie ? "Déplier le menu" : "Replier le menu";
      b.setAttribute("aria-expanded", replie ? "false" : "true");
      b.setAttribute("aria-label", (b.dataset.produit || "Documentation") + " — " + libelle.toLowerCase());
      b.setAttribute("title", libelle);
    });
  }
  function elementLu() {
    var hautEntete = (document.querySelector(".md-header") || {}).offsetHeight || 0;
    var blocs = document.querySelectorAll(".md-content__inner > *");
    for (var i = 0; i < blocs.length; i++) {
      if (blocs[i].getBoundingClientRect().bottom > hautEntete + 8) return blocs[i];
    }
    return null;
  }
  function brancherRepli() {
    appliquerRepli(lireRepli());
    document.querySelectorAll(".facil-marque__bascule").forEach(function (b) {
      if (b.dataset.branche) return;
      b.dataset.branche = "1";
      b.addEventListener("click", function () {
        // Le contenu s'élargit ou se resserre : on garde sous les yeux l'élément qu'on lisait.
        var repere = elementLu(), decalage = repere ? repere.getBoundingClientRect().top : 0;
        var replie = !document.documentElement.classList.contains("facil-nav-repliee");
        appliquerRepli(replie);
        ecrireRepli(replie);
        mesurerBarre();
        if (repere) window.scrollBy(0, repere.getBoundingClientRect().top - decalage);
      });
    });
  }
  // Un autre onglet replie ou déplie : on suit.
  window.addEventListener("storage", function (e) {
    if (e.key === "facil.nav.repliee") appliquerRepli(e.newValue === "1");
  });

  // --- 3. Diagrammes en grand -------------------------------------------------------------
  var dialogue, corps, niveau, declencheur, compteur = 0, zoom = 1;

  function themeMermaid() {
    var sombre = document.body.getAttribute("data-md-color-scheme") === "slate";
    return {
      startOnLoad: false,
      theme: "base",
      themeVariables: sombre ? {
        primaryColor: "#26341a", primaryTextColor: "#e6f2d9", primaryBorderColor: "#7CC242",
        lineColor: "#7CC242", secondaryColor: "#1e2029", tertiaryColor: "#2a2d38",
        background: "#1e2029", mainBkg: "#26341a", fontFamily: "Segoe UI, system-ui, sans-serif", fontSize: "16px"
      } : {
        primaryColor: "#eef6e6", primaryTextColor: "#1d3502", primaryBorderColor: "#397004",
        lineColor: "#397004", secondaryColor: "#ffffff", tertiaryColor: "#f6f8f4",
        background: "#ffffff", mainBkg: "#eef6e6", fontFamily: "Segoe UI, system-ui, sans-serif", fontSize: "16px"
      }
    };
  }

  function creerDialogue() {
    if (dialogue) return;
    dialogue = document.createElement("dialog");
    dialogue.className = "diagramme-plein";
    dialogue.setAttribute("aria-label", "Diagramme agrandi");
    dialogue.innerHTML =
      '<div class="diagramme-plein__barre">' +
      '<span class="diagramme-plein__titre">Diagramme</span>' +
      '<div class="diagramme-plein__outils" role="group" aria-label="Zoom">' +
      '<button type="button" data-action="moins" aria-label="Réduire">' + icone("moins") + "</button>" +
      '<span class="diagramme-plein__niveau" aria-live="polite">100 %</span>' +
      '<button type="button" data-action="plus" aria-label="Agrandir">' + icone("plus") + "</button>" +
      '<button type="button" data-action="ajuster" aria-label="Ajuster à l\'écran">' + icone("ajuster") + "</button>" +
      '<button type="button" data-action="fermer" class="diagramme-plein__fermer" aria-label="Fermer (Échap)">' + icone("fermer") + "<span>Fermer</span></button>" +
      "</div></div>" +
      '<div class="diagramme-plein__corps" tabindex="0"></div>';
    document.body.appendChild(dialogue);
    corps = dialogue.querySelector(".diagramme-plein__corps");
    niveau = dialogue.querySelector(".diagramme-plein__niveau");
    dialogue.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-action]");
      if (b) {
        var a = b.dataset.action;
        if (a === "fermer") return dialogue.close();
        if (a === "plus") return poserZoom(zoom + 0.25);
        if (a === "moins") return poserZoom(zoom - 0.25);
        if (a === "ajuster") return poserZoom(1);
      }
      if (e.target === dialogue) dialogue.close(); // clic sur le fond
    });
    dialogue.addEventListener("keydown", function (e) {
      if (e.key === "+" || e.key === "=") { poserZoom(zoom + 0.25); e.preventDefault(); }
      if (e.key === "-") { poserZoom(zoom - 0.25); e.preventDefault(); }
      if (e.key === "0") { poserZoom(1); e.preventDefault(); }
    });
    dialogue.addEventListener("close", function () {
      corps.innerHTML = "";
      document.documentElement.classList.remove("facil-dialogue-ouvert");
      if (declencheur) declencheur.focus();
    });
  }

  function poserZoom(z) {
    zoom = Math.min(4, Math.max(0.5, Math.round(z * 100) / 100));
    var svg = corps.querySelector("svg");
    if (svg) svg.style.width = (zoom * 100) + "%";
    niveau.textContent = Math.round(zoom * 100) + " %";
  }

  function ouvrir(figure) {
    var source = figure.querySelector(".diagramme__source");
    if (!source || typeof mermaid === "undefined") return;
    creerDialogue();
    declencheur = figure.querySelector(".diagramme__agrandir");
    var titre = figure.closest("article");
    var h = figure.previousElementSibling;
    while (h && !/^H[1-6]$/.test(h.tagName)) h = h.previousElementSibling;
    dialogue.querySelector(".diagramme-plein__titre").textContent =
      h ? h.textContent.replace(/¶\s*$/, "").trim() : (titre ? document.title : "Diagramme");
    corps.innerHTML = '<p class="diagramme-plein__attente">Préparation du diagramme…</p>';
    document.documentElement.classList.add("facil-dialogue-ouvert");
    dialogue.showModal();
    mermaid.initialize(themeMermaid());
    compteur += 1;
    mermaid.render("facil-diagramme-" + compteur, source.textContent).then(function (r) {
      corps.innerHTML = r.svg;
      var svg = corps.querySelector("svg");
      svg.removeAttribute("height");
      svg.style.maxWidth = "none";
      svg.style.height = "auto";
      poserZoom(1);
      dialogue.querySelector(".diagramme-plein__fermer").focus();
    }).catch(function () {
      corps.innerHTML = '<p class="diagramme-plein__attente">Ce diagramme n\'a pas pu être agrandi. Il reste lisible dans la page.</p>';
    });
  }

  function brancherDiagrammes() {
    document.querySelectorAll("figure.diagramme").forEach(function (f) {
      if (f.dataset.branche) return;
      f.dataset.branche = "1";
      f.addEventListener("click", function (e) {
        if (e.target.closest("a")) return;
        ouvrir(f);
      });
    });
  }

  // --- 4. Largeur réelle de la barre, reportée sur l'en-tête et le contenu -------------------
  function mesurerBarre() {
    var barre = document.querySelector(".md-sidebar--primary");
    if (!barre) return;
    var visible = window.matchMedia("(min-width: 76.25em)").matches;
    document.documentElement.style.setProperty("--facil-largeur-barre",
      visible ? Math.ceil(barre.getBoundingClientRect().width) + "px" : "0px");
  }
  var observateur = typeof ResizeObserver !== "undefined" ? new ResizeObserver(mesurerBarre) : null;
  function observerBarre() {
    var b = document.querySelector(".md-sidebar--primary");
    if (observateur && b && !b.dataset.observee) { b.dataset.observee = "1"; observateur.observe(b); }
  }
  window.addEventListener("resize", mesurerBarre);

  // --- 5. Chemin de la page dans l'en-tête : « Section › Page » ------------------------------
  function poserChemin() {
    var sujet = document.querySelector('.md-header__topic[data-md-component="header-topic"] .md-ellipsis');
    var actif = document.querySelector(".md-nav--primary .md-nav__link--active");
    if (!sujet || !actif || sujet.dataset.chemin) return;
    var sections = [];
    var item = actif.closest(".md-nav__item");
    var parent = item && item.parentElement ? item.parentElement.closest(".md-nav__item--nested, .md-nav__item--section") : null;
    while (parent) {
      var libelle = parent.querySelector(":scope > .md-nav__link, :scope > label.md-nav__link");
      if (libelle) sections.unshift(libelle.textContent.trim());
      parent = parent.parentElement ? parent.parentElement.closest(".md-nav__item--nested, .md-nav__item--section") : null;
    }
    var page = sujet.textContent.trim();
    sujet.textContent = "";
    sections.forEach(function (s) {
      var span = document.createElement("span");
      span.className = "facil-chemin";
      span.textContent = s;
      var sep = document.createElement("span");
      sep.className = "facil-chemin__sep";
      sep.setAttribute("aria-hidden", "true");
      sep.textContent = "›";
      sujet.appendChild(span);
      sujet.appendChild(sep);
    });
    sujet.appendChild(document.createTextNode(page));
    sujet.dataset.chemin = "1";
  }

  function initialiser() {
    poserAnnee();
    brancherRepli();
    brancherDiagrammes();
    poserChemin();
    observerBarre();
    mesurerBarre();
  }
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(initialiser);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialiser);
  } else {
    initialiser();
  }
})();
