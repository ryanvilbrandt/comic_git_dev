<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="/{{ base_dir }}/src/css/style.css">
    <link rel="stylesheet" type="text/css" href="/{{ base_dir }}/your_content/colors_and_layout/your_stylesheet.css">
    <link rel="icon" href="/{{ base_dir }}/favicon.ico" type="image/x-icon" />
    <title>{{ page_title }}</title>
</head>
<body>
<div id="container">
    <div id="banner"><img id="banner-img" src="/{{ base_dir }}/your_content/images/banner.png"></div>
    <div id="links-bar">
        {% for link in links %}
            <a class="link-bar-link" href="{{ link.url }}">{{ link.name }}</a>
            {% if not loop.last %}&nbsp;&nbsp;|&nbsp;&nbsp;{% endif %}
        {% endfor %}
    </div>

    <h1 id="page-title">Archive</h1>

    <div id="blurb">
        <ul>
        {% for section in archive_sections %}
            <li>{{ section.name }}
                <ul>
                {% for page in section.pages %}
                    <li><a href="/{{ base_dir }}/comic/{{ page.page_name }}.html">{{ page.page_title }}</a> -- {{ page.post_date }}</li>
                {% endfor %}
                </ul>
            </li>
        {% endfor %}
        </ul>
    </div>

    <div id="powered-by">
        Powered by <a id="powered-by-link" href="https://github.com/ryanvilbrandt/comic_git">comic_git</a>
    </div>
</div>
</body>
</html>
