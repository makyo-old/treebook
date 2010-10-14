from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter(name='comments')
def comments(value):
    return mark_safe(_treeify(value.comment_set.filter(parent__isnull = True), 0))

@register.filter(name='screened_comments')
def screened_comments(value):
    return mark_safe(_treeify(value.comment_set.filter(parent__isnull = True).filter(published = True), 0))

def _treeify(comments, indent):
    text = '<table>'
    i = 1
    for c in comments:
        text += """
        <tr>
            <td>
                <div class="comment %(cycle)s" style="padding-left: %(indent)sem"><a name="%(id)s" /><strong>%(title)s</strong> - %(poster)s
                <hr>
                %(body)s
                </div>
        """ % {'cycle': i % 2 == 0 and 'even' or 'odd', 'id': c.id, 'indent': indent, 'title': c.title, 'poster': c.owner.username, 'body': c.body}
        text += _treeify(c.comment_set.all(), indent + 1.5) + """
            </td>
        </tr>"""
    text += "</table>"
    i += 1
    return text
