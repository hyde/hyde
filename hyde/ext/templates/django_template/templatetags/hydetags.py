from django import template
from django.template import TemplateSyntaxError


register = template.Library()

class URLNode(template.Node):
      def __init__(self,path):
          self.path = path
      
      def render(self,context):
          pass

class ContentURLNode(URLNode):
      def  __init__(self,path):
           super(ContentURLNode,self).__init__(path)
     
      def render(self,context):
           return context['site'].content_url(self.path)

class MediaURLNode(URLNode):
      def  __init__(self,path):
           super(MediaURLNode,self).__init__(path)

      def render(self,context):
           return context['site'].media_url(self.path)

class FullURLNode(URLNode):
      def  __init__(self,path):
           super(FullURLNode,self).__init__(path)

      def render(self,context):
           return context['site'].full_url(self.path)

@register.tag(name="media_url")
def media_url(parser,token):
    try:
       urltag , path = token.split_contents();
    except ValueError:
       msg = '%r tag requires a single argument' % token.contents[0]
       raise template.TemplateSyntaxError(msg)
    return MediaURLNode(path[1:-1])

@register.tag(name="content_url")
def content_url(parser,token):
    try:
       urltag , path = token.split_contents();
    except ValueError:
       msg = '%r tag requires a single argument' % token.contents[0]
       raise template.TemplateSyntaxError(msg)
    return ContentURLNode(path[1:-1])

@register.tag(name="full_url")
def full_url(parser,token):
    try:
       urltag , path = token.split_contents();
    except ValueError:
       msg = '%r tag requires a single argument' % token.contents[0]
       raise template.TemplateSyntaxError(msg)
    return FullURLNode(path[1:-1])
