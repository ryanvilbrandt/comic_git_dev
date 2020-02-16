<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="/{{ base_dir }}/src/css/style.css">
    <link rel="stylesheet" type="text/css" href="/{{ base_dir }}/your_content/colors_and_layout/your_stylesheet.css">
    <link rel="icon" href="/{{ base_dir }}/favicon.ico" type="image/x-icon" />
    <title>{{ page_title }} - {{ comic_title }}</title>
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

    <div id="comic-page">
        <a href="{{ next_id }}.html"><img id="comic-image" src="{{ comic_path }}" title="{{ alt_text }}"/></a>
    </div>

    <div id="navigation-bar">
        <table id="navigation-buttons">
            <tr>
                <td id="navigation-button-first">
                    <a class="navigation-button" href="{{ first_id }}.html">First</a>
                </td>
                <td id="navigation-button-previous">
                    <a class="navigation-button" href="{{ previous_id }}.html">Previous</a>
                </td>
                <td id="navigation-button-next">
                    <a class="navigation-button" href="{{ next_id }}.html">Next</a>
                </td>
                <td id="navigation-button-last">
                    <a class="navigation-button" href="{{ last_id }}.html">Last</a>
                </td>
            </tr>
        </table>
    </div>

    <div id="blurb">
        <h1 id="page-title">{{ page_title }}</h1>
        <div id="post-date">Posted on: {{ post_date }}</div>
        <div id="tags">
            Tags:
            {% for tag in tags %}
                <a class="tag-link" href="/{{ base_dir }}/tagged.html?tag={{ tag }}">{{ tag }}</a>
                {% if not loop.last %}, {% endif %}
            {% endfor %}
        </div>
        <hr id="post-body-break">
        <div id="post-body">
            {{ post_html }}
        </div>
    </div>

    <div id="powered-by">
        Powered by <a id="powered-by-link" href="https://github.com/ryanvilbrandt/comic_git">comic_git</a>
    </div>
</div>
</body>
</html>
