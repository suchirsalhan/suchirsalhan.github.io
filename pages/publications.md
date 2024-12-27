---
layout: page
title: Research
permalink: "/publications/"
usemathjax: true
---
<!-- <h2 style="text-align: center;" >🚧 This Area Is Currently Under Construction 🚧 <br> ... Please visit again soon ...</h2> -->

<!-- <section #class="row"> -->

<h4 style="text-align: lefts;" >Conference & Journals</h4> 
{% assign i = 0 %}  
  {% for post in site.posts %}
      {% if post.featured == true %}
           {% if post.thesis != true %}
              {% if post.software != true %}
                {% include pub_menu.html %}
                
                {% assign i = i | plus:1 %}
            {% endif %}
            {% endif %}
      {% endif %}
  {% endfor %}

<h4 style="text-align: lefts;" >Thesis & Projects</h4> 


{% assign i = 0 %}  
  {% for post in site.posts %}
      {% if post.thesis == true %}
           
            {% include pub_menu.html %}
            
            {% assign i = i | plus:1 %}
      {% endif %}
  {% endfor %}

<!-- <h4 style="text-align: lefts;" >Software</h4>  -->


{% assign i = 0 %}  
  {% for post in site.posts %}
      {% if post.software == true %}
           
            {% include pub_menu.html %}
            
            {% assign i = i | plus:1 %}
      {% endif %}
  {% endfor %}
<!-- </section> -->
 <!-- <div class="col-md-4 mb-5"> -->
 <!-- </div> -->