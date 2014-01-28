def setup(app):
    app.add_crossref_type(
        directivename="setting",
        rolename="setting",
        indextemplate="pair: %s; setting",
    )

    app.add_crossref_type(
        directivename="django-admin",
        rolename="djadmin",
    )

    app.add_crossref_type(
        directivename = "templatetag",
        rolename      = "ttag",
        indextemplate = "pair: %s; template tag"
    )
