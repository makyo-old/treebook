import re
from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter(name='stripbb')
@stringfilter
def stripbb(value):
    bbdata = [
            (r'\[badger\](.+?)\[/badger]', r'Check to see where else you can find me on <a target="_blank" href="http://badger.mjs-svc.com/badger/\1/">Badger!</a>'),
            (r'\[url\](.+?)\[/url\]', r'<a rel="nofollow" href="\1">\1</a>'),
            (r'\[url=(.+?)\](.+?)\[/url\]', r'<a rel="nofollow" href="\1">\2</a>'),
            (r'\[email\](.+?)\[/email\]', r'<a href="mailto:\1">\1</a>'),
            (r'\[email=(.+?)\](.+?)\[/email\]', r'<a href="mailto:\1">\2</a>'),
            (r'\[img\](.+?)\[/img\]', r'[IMAGE]'),
            (r'\[img=(.+?)\](.+?)\[/img\]', r'[IMAGE]'),
            (r'\[b\](.+?)\[/b\]', r'<strong>\1</strong>'),
            (r'\[i\](.+?)\[/i\]', r'<em>\1</em>'),
            (r'\[u\](.+?)\[/u\]', r'<span style="text-decoration: underline;">\1</span>'),
            (r'\[quote\](.+?)\[/quote\]', r'\1'),
            (r'\[quote=(.+?)\](.+?)\[/quote\]', r'Quote: \1 -- \2'),
            (r'\[center\](.+?)\[/center\]', r'\1'),
            (r'\[code\](.+?)\[/code\]', r'\1'),
            (r'\[big\](.+?)\[/big\]', r'\1'),
            (r'\[small\](.+?)\[/small\]', r'\1'),
            (r'\[list\](.+?)\[/list\]', r''),
            (r'\[list=(.)\](.+?)\[/list\]', r''),
        ]

    for bbset in bbdata:
        p = re.compile(bbset[0], re.DOTALL)
        value = p.sub(bbset[1], value)

    p = re.compile(r'\[quote\](.+?)\[/quote\]')
    while p.search(value):
        value = p.sub(r'<div class="post-quote"><span class="quote-header">Quote</span>\1</div>', value)

    p = re.compile(r'\[quote=(.+?)\](.+?)\[/quote\]')
    while p.search(value):
        value = p.sub(r'<div class="post-quote"><span class="quote-header">Quote: \1</span>\2</div>', value)
    #The following two code parts handle the more complex list statements
    temp = ''
    p = re.compile(r'\[list\](.+?)\[/list\]', re.DOTALL)
    m = p.search(value)
    if m:
        items = re.split(re.escape('[*]'), m.group(1))
        for i in items[1:]:
            temp = temp + '<li>' + i + '</li>'
        value = p.sub(r'<ul>'+temp+'</ul>', value)

    temp = ''
    p = re.compile(r'\[list=(.)\](.+?)\[/list\]', re.DOTALL)
    m = p.search(value)
    if m:
        items = re.split(re.escape('[*]'), m.group(2))
        for i in items[1:]:
            temp = temp + '<li>' + i + '</li>'
        value = p.sub(r'<ol type="\1">'+temp+'</ol>', value)

    return value

@register.filter(name='bbcode')
@stringfilter
def bbcode(value):

    bbdata = [
        (r'\[badger\](.+?)\[/badger]', r'<link rel="stylesheet" type="text/css" href="http://mjs-svc.com/badger/badge.css" /><span class="badgerjax-\1"></span><script type="text/javascript" src="http://mjs-svc.com/js/jquery-1.4.2.min.js"></script><script type="text/javascript" src="http://badger.mjs-svc.com/b/\1/"></script>'),
        (r'\[url\](.+?)\[/url\]', r'<a rel="nofollow" href="\1">\1</a>'),
        (r'\[url=(.+?)\](.+?)\[/url\]', r'<a rel="nofollow" href="\1">\2</a>'),
        (r'\[email\](.+?)\[/email\]', r'<a href="mailto:\1">\1</a>'),
        (r'\[email=(.+?)\](.+?)\[/email\]', r'<a href="mailto:\1">\2</a>'),
        (r'\[img\](.+?)\[/img\]', r'<img src="\1" />'),
        (r'\[img=(.+?)\](.+?)\[/img\]', r'<img src="\1" alt="\2" />'),
        (r'\[b\](.+?)\[/b\]', r'<strong>\1</strong>'),
        (r'\[i\](.+?)\[/i\]', r'<em>\1</em>'),
        (r'\[u\](.+?)\[/u\]', r'<span style="text-decoration: underline;">\1</span>'),
        #(r'\[quote\](.+?)\[/quote\]', r'<div class="post-quote"><span class="quote-header">Quote</span>\1</div>'),
        #(r'\[quote=(.+?)\](.+?)\[/quote\]', r'<div class="post-quote"><span class="quote-header">Quote: \1</span>\2</div>'),
        (r'\[center\](.+?)\[/center\]', r'<div style="text-align: center">\1</div>'),
        (r'\[code\](.+?)\[/code\]', r'<pre>\1</pre>'),
        (r'\[big\](.+?)\[/big\]', r'<span style="font-size: 120%">\1</span>'),
        (r'\[small\](.+?)\[/small\]', r'<span style="font-size: 75%">\1</span>'),
        (r'\n', r'<br />'),
        ]

    for bbset in bbdata:
        p = re.compile(bbset[0], re.DOTALL)
        value = p.sub(bbset[1], value)

    p = re.compile(r'\[quote\](.+?)\[/quote\]')
    while p.search(value):
        value = p.sub(r'<div class="post-quote"><span class="quote-header">Quote</span>\1</div>', value)

    p = re.compile(r'\[quote=(.+?)\](.+?)\[/quote\]')
    while p.search(value):
        value = p.sub(r'<div class="post-quote"><span class="quote-header">Quote: \1</span>\2</div>', value)
    #The following two code parts handle the more complex list statements
    temp = ''
    p = re.compile(r'\[list\](.+?)\[/list\]', re.DOTALL)
    m = p.search(value)
    if m:
        items = re.split(re.escape('[*]'), m.group(1))
        for i in items[1:]:
            temp = temp + '<li>' + i + '</li>'
        value = p.sub(r'<ul>'+temp+'</ul>', value)

    temp = ''
    p = re.compile(r'\[list=(.)\](.+?)\[/list\]', re.DOTALL)
    m = p.search(value)
    if m:
        items = re.split(re.escape('[*]'), m.group(2))
        for i in items[1:]:
            temp = temp + '<li>' + i + '</li>'
        value = p.sub(r'<ol type="\1">'+temp+'</ol>', value)

    return value
