/* SANAYA — global theme interactions */
(function () {
  "use strict";

  var routes = window.SANAYA_ROUTES || { cart_add: "/cart/add.js", cart_change: "/cart/change.js", cart: "/cart.js" };

  /* ---------- helpers ---------- */
  function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
  function qsa(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function trapFocus(container) {
    var focusable = qsa('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])', container)
      .filter(function (el) { return !el.disabled && el.offsetParent !== null; });
    if (!focusable.length) return function () {};
    var first = focusable[0], last = focusable[focusable.length - 1];
    function handler(e) {
      if (e.key !== "Tab") return;
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
    container.addEventListener("keydown", handler);
    first.focus();
    return function () { container.removeEventListener("keydown", handler); };
  }

  /* ---------- overlay (shared by mobile menu, filters, cart) ---------- */
  var overlay = qs(".js-overlay");
  var openPanels = [];
  function showOverlay() { if (overlay) overlay.classList.add("is-visible"); document.documentElement.style.overflow = "hidden"; }
  function hideOverlay() { if (overlay) overlay.classList.remove("is-visible"); document.documentElement.style.overflow = ""; }

  function openPanel(panel) {
    panel.classList.add("is-open");
    panel.removeAttribute("hidden");
    showOverlay();
    var release = trapFocus(panel);
    openPanels.push({ panel: panel, release: release });
  }
  function closePanel(panel) {
    panel.classList.remove("is-open");
    openPanels = openPanels.filter(function (p) {
      if (p.panel === panel) { p.release(); return false; }
      return true;
    });
    if (!openPanels.length) hideOverlay();
  }
  function closeAllPanels() {
    openPanels.slice().forEach(function (p) { closePanel(p.panel); });
  }
  if (overlay) overlay.addEventListener("click", closeAllPanels);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeAllPanels();
  });

  qsa("[data-open-panel]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = document.getElementById(btn.getAttribute("data-open-panel"));
      if (target) openPanel(target);
    });
  });
  qsa("[data-close-panel]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = btn.closest("[data-panel]") || document.getElementById(btn.getAttribute("data-close-panel"));
      if (target) closePanel(target);
    });
  });

  /* ---------- sticky header shrink ---------- */
  var header = qs(".site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-stuck", window.scrollY > 8);
    };
    document.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- mega menu (keyboard + hover already CSS; add click-toggle for touch) ---------- */
  qsa(".nav-item").forEach(function (item) {
    var trigger = qs(".site-header__nav-link", item);
    if (!trigger) return;
    trigger.addEventListener("click", function (e) {
      var menu = qs(".mega-menu", item);
      if (!menu) return;
      if (window.matchMedia("(hover: hover)").matches) return;
      e.preventDefault();
      var isOpen = item.classList.contains("is-open");
      qsa(".nav-item.is-open").forEach(function (i) { i.classList.remove("is-open"); });
      if (!isOpen) item.classList.add("is-open");
    });
  });

  /* ---------- accordion ---------- */
  qsa(".accordion__trigger").forEach(function (trigger) {
    var panel = document.getElementById(trigger.getAttribute("aria-controls"));
    if (!panel) return;
    trigger.addEventListener("click", function () {
      var expanded = trigger.getAttribute("aria-expanded") === "true";
      trigger.setAttribute("aria-expanded", String(!expanded));
      panel.style.maxHeight = expanded ? "0px" : panel.scrollHeight + "px";
    });
  });

  /* ---------- scroll reveal ---------- */
  var revealEls = qsa("[data-reveal]");
  if (revealEls.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- testimonial slider ---------- */
  qsa("[data-testimonial-slider]").forEach(function (slider) {
    var slides = qsa(".testimonial-slide", slider);
    var dots = qsa(".testimonial-nav__dot", slider);
    var index = 0, timer;
    function show(i) {
      index = (i + slides.length) % slides.length;
      slides.forEach(function (s, si) { s.classList.toggle("is-active", si === index); });
      dots.forEach(function (d, di) { d.classList.toggle("is-active", di === index); });
    }
    dots.forEach(function (dot, i) {
      dot.addEventListener("click", function () { show(i); restart(); });
    });
    function restart() {
      clearInterval(timer);
      timer = setInterval(function () { show(index + 1); }, 6000);
    }
    if (slides.length) { show(0); restart(); }
  });

  /* ---------- quantity steppers ---------- */
  qsa("[data-qty-stepper]").forEach(function (stepper) {
    var input = qs("input", stepper);
    qsa("button", stepper).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var step = parseInt(input.step || "1", 10);
        var min = parseInt(input.min || "1", 10);
        var val = parseInt(input.value || "1", 10);
        val = btn.getAttribute("data-action") === "increase" ? val + step : Math.max(min, val - step);
        input.value = val;
        input.dispatchEvent(new Event("change", { bubbles: true }));
      });
    });
  });

  /* ---------- product gallery thumbs ---------- */
  qsa("[data-gallery]").forEach(function (gallery) {
    var main = qs("[data-gallery-main] img", gallery);
    qsa("[data-gallery-thumb]", gallery).forEach(function (thumb) {
      thumb.addEventListener("click", function () {
        qsa("[data-gallery-thumb]", gallery).forEach(function (t) { t.classList.remove("is-active"); });
        thumb.classList.add("is-active");
        if (main && thumb.getAttribute("data-full")) main.src = thumb.getAttribute("data-full");
      });
    });
  });

  /* ---------- variant swatches ---------- */
  qsa("[data-swatch-group]").forEach(function (group) {
    qsa(".swatch", group).forEach(function (swatch) {
      swatch.addEventListener("click", function () {
        if (swatch.classList.contains("is-disabled")) return;
        qsa(".swatch", group).forEach(function (s) { s.classList.remove("is-selected"); });
        swatch.classList.add("is-selected");
        var hiddenInput = qs('input[name="' + group.getAttribute("data-swatch-group") + '"]', group.closest("form") || document);
        if (hiddenInput) hiddenInput.value = swatch.getAttribute("data-value");
      });
    });
  });

  /* ---------- sticky add-to-cart bar (PDP mobile) ---------- */
  var stickyBar = qs(".pdp__sticky-bar");
  var pdpForm = qs("[data-pdp-form]");
  if (stickyBar && pdpForm && "IntersectionObserver" in window) {
    var pdpIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        stickyBar.classList.toggle("is-visible", !entry.isIntersecting && window.innerWidth < 990);
      });
    }, { threshold: 0 });
    pdpIo.observe(pdpForm);
  }

  /* ---------- cart drawer AJAX ---------- */
  var cartDrawer = qs("#cart-drawer");
  var cartCountEls = qsa("[data-cart-count]");

  function updateCartCount(count) {
    cartCountEls.forEach(function (el) {
      el.textContent = count;
      el.hidden = count === 0;
    });
  }

  function renderCartDrawer(cart) {
    if (!cartDrawer) return;
    var body = qs("[data-cart-drawer-body]", cartDrawer);
    var footer = qs("[data-cart-drawer-footer]", cartDrawer);
    var fill = qs("[data-shipping-fill]", cartDrawer);
    var shippingText = qs("[data-shipping-text]", cartDrawer);
    var threshold = parseFloat(cartDrawer.getAttribute("data-free-shipping-threshold") || "0") * 100;

    if (!cart.items.length) {
      if (body) body.innerHTML = qs("[data-cart-empty-template]").innerHTML;
      if (footer) footer.hidden = true;
      updateCartCount(0);
      return;
    }
    if (footer) footer.hidden = false;

    if (threshold > 0) {
      var remaining = Math.max(0, threshold - cart.total_price);
      var pct = Math.min(100, (cart.total_price / threshold) * 100);
      if (fill) fill.style.width = pct + "%";
      if (shippingText) {
        shippingText.textContent = remaining === 0
          ? shippingText.getAttribute("data-reached")
          : shippingText.getAttribute("data-remaining-template").replace("{amount}", formatMoney(remaining));
      }
    }

    if (body) {
      body.innerHTML = cart.items.map(function (item) {
        return (
          '<div class="cart-line" data-line-key="' + item.key + '">' +
            '<a href="' + item.url + '" class="media cart-line__media media--square">' +
              (item.image ? '<img src="' + item.image + '" alt="' + escapeHtml(item.product_title) + '" loading="lazy">' : "") +
            "</a>" +
            '<div class="cart-line__content">' +
              '<a href="' + item.url + '" class="cart-line__title">' + escapeHtml(item.product_title) + "</a>" +
              (item.variant_title ? '<div class="cart-line__variant">' + escapeHtml(item.variant_title) + "</div>" : "") +
              '<div class="cart-line__footer">' +
                '<div class="qty-stepper" data-qty-stepper data-line-key="' + item.key + '">' +
                  '<button type="button" data-action="decrease" aria-label="Decrease quantity">−</button>' +
                  '<input type="text" inputmode="numeric" value="' + item.quantity + '" min="0" aria-label="Quantity" readonly>' +
                  '<button type="button" data-action="increase" aria-label="Increase quantity">+</button>' +
                "</div>" +
                '<span class="cart-line__price">' + formatMoney(item.final_line_price) + "</span>" +
              "</div>" +
            "</div>" +
          "</div>"
        );
      }).join("");
    }
    var subtotalEl = qs("[data-cart-subtotal]", cartDrawer);
    if (subtotalEl) subtotalEl.textContent = formatMoney(cart.total_price);
    updateCartCount(cart.item_count);

    qsa("[data-qty-stepper]", body).forEach(function (stepper) {
      var key = stepper.getAttribute("data-line-key");
      var input = qs("input", stepper);
      qsa("button", stepper).forEach(function (btn) {
        btn.addEventListener("click", function () {
          var val = parseInt(input.value, 10);
          val = btn.getAttribute("data-action") === "increase" ? val + 1 : val - 1;
          changeLine(key, val);
        });
      });
    });
  }

  function formatMoney(cents) {
    return "$" + (cents / 100).toFixed(2);
  }
  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
  }

  function fetchCart() {
    return fetch(routes.cart + ".js").then(function (r) { return r.json(); }).then(renderCartDrawer);
  }

  function changeLine(key, quantity) {
    return fetch(routes.cart_change, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ id: key, quantity: quantity }),
    }).then(function (r) { return r.json(); }).then(renderCartDrawer);
  }

  qsa("form[data-cart-add-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var submitBtn = qs('[type="submit"]', form);
      if (submitBtn) submitBtn.disabled = true;
      var formData = new FormData(form);
      fetch(routes.cart_add, {
        method: "POST",
        headers: { Accept: "application/json" },
        body: formData,
      })
        .then(function (r) { return r.json(); })
        .then(function () {
          if (cartDrawer) {
            fetchCart().then(function () { openPanel(cartDrawer); });
          }
        })
        .catch(function () { form.submit(); })
        .finally(function () { if (submitBtn) submitBtn.disabled = false; });
    });
  });

  qsa("[data-cart-line-remove]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      changeLine(btn.getAttribute("data-cart-line-remove"), 0);
    });
  });

  if (cartDrawer) fetchCart();

  /* ---------- newsletter inline success (progressive enhancement, native fallback) ---------- */
  qsa("[data-newsletter-form]").forEach(function (form) {
    form.addEventListener("submit", function () {
      form.setAttribute("data-submitting", "true");
    });
  });
})();
