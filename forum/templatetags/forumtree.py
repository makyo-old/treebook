from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter(name='forumtree')
def forumtree(value):
    return mark_safe(_treeify(value, 0))

def _treeify(forum, indent):
    text = ''
    for f in forum.forum_set.all():
        text += """
        <tr class="forumlisting">
            <td><div style="padding-left: %(indent)sem"><strong><a href="%(furl)s">%(fname)s</a></strong><br />
                %(fdesc)s</div></td>
            <td class="pcount">%(fpcount)s</td>
        </tr>
        """ % {'indent': indent, 'furl': f.get_absolute_url(), 'fname': f.name, 'fdesc': f.description, 'fpcount': not f.users_can_post and '<em>Locked</em>' or f.post_set.count()}
        text += _treeify(f, indent + 1.5)
    return text

