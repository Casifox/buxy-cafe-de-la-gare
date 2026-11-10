/* ==========================================================================
   Pizzeria Café de la Gare — interactions
   Aucune dépendance externe. Tout est progressif : le site reste lisible
   sans JavaScript.
   ========================================================================== */
(() => {
  "use strict";

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  document.documentElement.classList.remove("no-js");
  document.documentElement.classList.add("js");

  /* ------------------------------------------------------------------------
     En-tête : état au défilement
     ------------------------------------------------------------------------ */
  const header = $("[data-header]");
  if (header) {
    const updateHeader = () => {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
    };
    updateHeader();
    window.addEventListener("scroll", updateHeader, { passive: true });
  }

  /* ------------------------------------------------------------------------
     Menu mobile (dialog natif)
     ------------------------------------------------------------------------ */
  const mobileNav = $("#mobile-nav");
  const navToggle = $(".nav-toggle");

  if (mobileNav && navToggle) {
    const openNav = () => {
      if (!mobileNav.open) mobileNav.showModal();
      navToggle.setAttribute("aria-expanded", "true");
      document.body.classList.add("nav-open");
    };

    const closeNav = () => {
      if (mobileNav.open) mobileNav.close();
      navToggle.setAttribute("aria-expanded", "false");
      document.body.classList.remove("nav-open");
    };

    navToggle.addEventListener("click", openNav);

    $$("[data-close]", mobileNav).forEach((element) => {
      element.addEventListener("click", closeNav);
    });

    mobileNav.addEventListener("close", () => {
      navToggle.setAttribute("aria-expanded", "false");
      document.body.classList.remove("nav-open");
      navToggle.focus();
    });

    mobileNav.addEventListener("click", (event) => {
      if (event.target === mobileNav) closeNav();
    });

    const desktopQuery = window.matchMedia("(min-width: 1025px)");
    desktopQuery.addEventListener("change", (event) => {
      if (event.matches) closeNav();
    });
  }

  /* ------------------------------------------------------------------------
     Statut d'ouverture — heure de Paris
     ------------------------------------------------------------------------ */
  const SCHEDULE = {
    0: { open: "15:30", close: "22:30" }, // dimanche
    1: null, // lundi
    2: { open: "08:30", close: "22:45" },
    3: { open: "08:30", close: "22:45" },
    4: { open: "08:30", close: "22:45" },
    5: { open: "08:30", close: "23:00" },
    6: { open: "15:30", close: "23:00" },
  };

  const DAY_NAMES = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];

  const toMinutes = (value) => {
    const [hours, minutes] = value.split(":").map(Number);
    return hours * 60 + minutes;
  };

  const formatTime = (value) => value.replace(":", "h").replace(/h00$/, "h");

  const getParisNow = () => {
    try {
      const formatter = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Europe/Paris",
        weekday: "long",
        hour: "2-digit",
        minute: "2-digit",
        hourCycle: "h23",
      });
      const parts = Object.fromEntries(
        formatter.formatToParts(new Date()).map((part) => [part.type, part.value])
      );
      const dayIndex = {
        Sunday: 0,
        Monday: 1,
        Tuesday: 2,
        Wednesday: 3,
        Thursday: 4,
        Friday: 5,
        Saturday: 6,
      }[parts.weekday];

      return {
        day: dayIndex,
        minutes: Number(parts.hour) * 60 + Number(parts.minute),
      };
    } catch {
      const now = new Date();
      return { day: now.getDay(), minutes: now.getHours() * 60 + now.getMinutes() };
    }
  };

  const getStatus = () => {
    const { day, minutes } = getParisNow();
    const today = SCHEDULE[day];

    if (today) {
      const open = toMinutes(today.open);
      const close = toMinutes(today.close);

      if (minutes >= open && minutes < close) {
        return {
          open: true,
          text: `Ouvert maintenant · jusqu’à ${formatTime(today.close)}`,
        };
      }

      if (minutes < open) {
        return {
          open: false,
          text: `Fermé · ouvre aujourd’hui à ${formatTime(today.open)}`,
        };
      }
    }

    for (let offset = 1; offset <= 7; offset += 1) {
      const nextDay = (day + offset) % 7;
      const next = SCHEDULE[nextDay];
      if (next) {
        const label = offset === 1 ? "demain" : DAY_NAMES[nextDay];
        return {
          open: false,
          text: `Fermé · réouverture ${label} à ${formatTime(next.open)}`,
        };
      }
    }

    return { open: false, text: "Fermé" };
  };

  const status = getStatus();
  $$("[data-open-status]").forEach((element) => {
    const label = $(".status__text", element) || element;
    label.textContent = status.text;
    element.classList.toggle("status--open", status.open);
    element.classList.toggle("status--closed", !status.open);
  });

  const { day: parisDay } = getParisNow();
  $$(".hours-table tr[data-day]").forEach((row) => {
    const rowDay = Number(row.dataset.day);
    row.classList.toggle("is-today", rowDay === parisDay);
  });

  /* ------------------------------------------------------------------------
     Apparition au défilement
     ------------------------------------------------------------------------ */
  const revealElements = $$(".reveal");
  if (revealElements.length) {
    if ("IntersectionObserver" in window) {
      const revealObserver = new IntersectionObserver(
        (entries, observer) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              observer.unobserve(entry.target);
            }
          });
        },
        { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
      );

      revealElements.forEach((element) => revealObserver.observe(element));
    } else {
      revealElements.forEach((element) => element.classList.add("is-visible"));
    }
  }

  /* ------------------------------------------------------------------------
     Galerie — lightbox accessible
     ------------------------------------------------------------------------ */
  const galleryTriggers = $$(".gallery__item");
  const lightbox = $("#lightbox");

  if (galleryTriggers.length && lightbox) {
    const images = galleryTriggers.map((trigger) => ({
      src: trigger.dataset.full,
      alt: trigger.dataset.alt || "",
      caption: trigger.dataset.caption || "",
    }));

    const lightboxImage = $("#lightbox-img");
    const lightboxCaption = $("#lightbox-caption");
    const lightboxCount = $("#lightbox-count");
    const closeButton = $("[data-lightbox-close]", lightbox);
    const prevButton = $("[data-lightbox-prev]", lightbox);
    const nextButton = $("[data-lightbox-next]", lightbox);
    let currentIndex = 0;
    let lastTrigger = null;

    const updateLightbox = (index) => {
      currentIndex = (index + images.length) % images.length;
      const image = images[currentIndex];
      lightboxImage.src = image.src;
      lightboxImage.alt = image.alt;
      lightboxCaption.textContent = image.caption;
      lightboxCount.textContent = `${currentIndex + 1} / ${images.length}`;

      // Précharge les images voisines pour une navigation fluide.
      [currentIndex + 1, currentIndex - 1].forEach((nextIndex) => {
        const nextImage = images[(nextIndex + images.length) % images.length];
        if (nextImage) {
          const preload = new Image();
          preload.src = nextImage.src;
        }
      });
    };

    const openLightbox = (index, trigger) => {
      lastTrigger = trigger || null;
      updateLightbox(index);
      if (!lightbox.open) lightbox.showModal();
      document.body.classList.add("modal-open");
    };

    const closeLightbox = () => {
      if (lightbox.open) lightbox.close();
      document.body.classList.remove("modal-open");
    };

    galleryTriggers.forEach((trigger, index) => {
      trigger.addEventListener("click", () => openLightbox(index, trigger));
    });

    $$("[data-open-gallery]").forEach((button) => {
      button.addEventListener("click", () => {
        const index = Number(button.dataset.openGallery) || 0;
        openLightbox(index, button);
      });
    });

    closeButton?.addEventListener("click", closeLightbox);
    prevButton?.addEventListener("click", () => updateLightbox(currentIndex - 1));
    nextButton?.addEventListener("click", () => updateLightbox(currentIndex + 1));

    lightbox.addEventListener("click", (event) => {
      if (event.target === lightbox) closeLightbox();
    });

    lightbox.addEventListener("close", () => {
      document.body.classList.remove("modal-open");
      lastTrigger?.focus();
    });

    lightbox.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        updateLightbox(currentIndex - 1);
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        updateLightbox(currentIndex + 1);
      }
    });

    let touchStartX = null;
    lightboxImage.addEventListener(
      "touchstart",
      (event) => {
        touchStartX = event.changedTouches[0].clientX;
      },
      { passive: true }
    );

    lightboxImage.addEventListener(
      "touchend",
      (event) => {
        if (touchStartX === null) return;
        const delta = event.changedTouches[0].clientX - touchStartX;
        if (Math.abs(delta) > 45) {
          updateLightbox(delta > 0 ? currentIndex - 1 : currentIndex + 1);
        }
        touchStartX = null;
      },
      { passive: true }
    );
  }

  /* ------------------------------------------------------------------------
     Navigation de la carte : section active
     ------------------------------------------------------------------------ */
  const menuNavLinks = $$(".menu-nav a[href^='#']");
  if (menuNavLinks.length && "IntersectionObserver" in window) {
    const sections = menuNavLinks
      .map((link) => document.querySelector(link.getAttribute("href")))
      .filter(Boolean);

    const navObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          menuNavLinks.forEach((link) => {
            link.removeAttribute("aria-current");
            if (link.getAttribute("href") === `#${entry.target.id}`) {
              link.setAttribute("aria-current", "true");
            }
          });
        });
      },
      { rootMargin: "-35% 0px -55% 0px", threshold: 0 }
    );

    sections.forEach((section) => navObserver.observe(section));
  }

  /* ------------------------------------------------------------------------
     Impression & année
     ------------------------------------------------------------------------ */
  $$("[data-print]").forEach((button) => {
    button.addEventListener("click", () => window.print());
  });

  $$("[data-year]").forEach((element) => {
    element.textContent = new Date().getFullYear();
  });
})();
