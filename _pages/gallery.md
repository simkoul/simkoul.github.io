---
permalink: /gallery/
title: "Gallery"
layout: splash
author_profile: false
published: false   # kept for later; photographs not ready yet
---

{% include base_path %}

<div class="wrap">

  <div class="band">
    <h1 class="display">Gallery</h1>
    <div class="col">
      <p class="aff">Field sites, and the places in between.</p>
    </div>
  </div>

  {% assign groups = site.data.photographs | group_by: "group" %}

  {% if groups.size > 0 %}
    {% for g in groups %}
    <div class="band">
      <div class="shead"><h2>{{ g.name }}</h2></div>
      <div class="gal">
        {% for photo in g.items %}
        <figure class="gal__item">
          <img src="{{ photo.image | prepend: '/images/elsewhere/' | prepend: base_path }}"
               alt="{{ photo.alt | default: photo.caption | escape }}"
               loading="lazy" decoding="async">
          {% if photo.caption %}<figcaption>{{ photo.caption }}</figcaption>{% endif %}
        </figure>
        {% endfor %}
      </div>
    </div>
    {% endfor %}
  {% else %}
    <div class="band">
      <div class="col"><p class="aff">Photographs going up here shortly.</p></div>
    </div>
  {% endif %}

</div>

<!-- Click any photograph to see it full size. -->
<div class="lb" id="lb" hidden>
  <button class="lb__close" type="button" aria-label="Close">&times;</button>
  <figure><img src="" alt=""><figcaption></figcaption></figure>
</div>

<script>
(function () {
  var lb = document.getElementById("lb");
  if (!lb) return;
  var img = lb.querySelector("img");
  var cap = lb.querySelector("figcaption");

  function close() { lb.hidden = true; document.body.style.overflow = ""; }

  document.querySelectorAll(".gal__item img").forEach(function (t) {
    t.addEventListener("click", function () {
      img.src = t.currentSrc || t.src;
      img.alt = t.alt;
      var f = t.closest("figure").querySelector("figcaption");
      cap.textContent = f ? f.textContent : "";
      lb.hidden = false;
      document.body.style.overflow = "hidden";
    });
  });

  lb.addEventListener("click", function (e) {
    if (e.target === lb || e.target.classList.contains("lb__close")) close();
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
})();
</script>
