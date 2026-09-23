---
permalink: /open-tabs/
title: "Open Tabs"
layout: splash
author_profile: false
published: false   # retired until the notes and reading list are your own
---

{% include base_path %}

<div class="wrap">

  <div class="band">
    <h1 class="display">Open Tabs</h1>
    <div class="col">
      <p>If any of this overlaps with what you think about, that is the entire point of
      the page, so say hello.</p>
    </div>
  </div>

  <div class="band">
    <div class="shead"><h2>Notes</h2></div>

    {% for note in site.data.thoughts %}
    <div class="think">
      <span class="when">{{ note.when }}</span>
      <div>
        <div class="what">{{ note.what }}</div>
        {% if note.tags %}
        <div class="tags">{% for t in note.tags %}<span class="tag">{{ t }}</span>{% endfor %}</div>
        {% endif %}
      </div>
    </div>
    {% endfor %}

    <div class="invite">
      Working on something adjacent to any of this? Please email me. I would happily be
      talked out of any of it.
      <a href="mailto:simran_koul@ucsb.edu">simran_koul@ucsb.edu</a>
    </div>
  </div>

  <div class="band">
    <div class="shead"><h2>Reading</h2></div>

    {% for book in site.data.reading %}
    <div class="book">
      <div class="book__title">{{ book.title }}<span class="book__author">{{ book.author }}</span></div>
      {% if book.note %}<p class="book__note">{{ book.note }}</p>{% endif %}
      {% if book.quote %}<blockquote class="book__quote">{{ book.quote }}</blockquote>{% endif %}
    </div>
    {% endfor %}
  </div>

</div>
