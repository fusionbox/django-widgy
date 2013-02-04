from django import forms
from django.template.defaultfilters import slugify


class ResourceForm(forms.ModelForm):
    #child_nodes = forms.ModelChoiceField(queryset=Node.objects.none())

    def __init__(self, *args, **kwargs):
        super(ResourceForm, self).__init__(*args, **kwargs)
        if self.instance:
            children = self.instance.node.get_children()
            if children:
                self.fields['child_nodes'] = forms.ModelMultipleChoiceField(
                    #widget=forms.CheckboxSelectMultiple,
                    queryset=children,
                )

    def save(self, *args, **kwargs):
        # TODO: make this work with commit = `False` and abstract it out of the form
        original = self.instance.__class__.objects.get(pk=self.instance.pk)
        instance = super(ResourceForm, self).save(*args, **kwargs)
        if original.slug and not instance.slug == original.slug:
            from widgy.contrib.site_builder.models import InternalRedirect
            new_redirect = original.get_parent().add_child(
                self.site,
                cls=InternalRedirect,
                slug=original.slug,
                target=instance.get_absolute_url(),
            )
            import pdb; pdb.set_trace()
            for node in self.cleaned_data.get('child_nodes', []):
                new_redirect.add_child(
                    self.site,
                    cls=InternalRedirect,
                    slug=node.content.slug,
                    target=node.content.get_absolute_url(),
                )
        return instance

    class Meta:
        exclude = ('root_node',)


class ContentPageForm(forms.ModelForm):
    class Meta:
        exclude = ('slug',)

    def validate_title(self):
        slug = slugify(self.cleaned_data['title'])
        if self.instance and self.instance.pk:
            self.instance.get_parent().validate_child_slug(slug, self.instance)
        return self.cleaned_data['title']

    def save(self, *args, **kwargs):
        if self.instance and self.instance.pk and not self.instance.slug:
            self.instance.slug = slugify(self.cleaned_data['title'])
        return super(ContentPageForm, self).save(*args, **kwargs)
