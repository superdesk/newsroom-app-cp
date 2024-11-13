def init_app(app):
    app.sidenav(
        name="CP Images",
        url="https://www.cpimages.com/",
        icon="photo",
        group=8,
        locale="en",
    )

    app.sidenav(
        name="PC Images",
        url="https://www.cpimages.com/CS.aspx?VP3=CMS3&VF=Home&LANGSWI=1&LANG=French",
        icon="photo",
        group=8,
        locale="fr_CA",
    )
