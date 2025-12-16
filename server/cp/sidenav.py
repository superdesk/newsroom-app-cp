def init_app(app):
    app.sidenav(
        name="CP Images",
        url="https://www.cpimages.com/",
        icon="photo",
        group=8,
        locale="en",
    )

    if app.config.get("PR_MANAGER_SIDENAV_ENABLED"):
        app.sidenav(
            name="PR Manager",
            url=app.config.get("PR_MANAGER_SIDENAV_URL"),
            icon="pr-manager",
        )

    app.sidenav(
        name="PC Images",
        url="https://www.cpimages.com/CS.aspx?VP3=CMS3&VF=Home&LANGSWI=1&LANG=French",
        icon="photo",
        group=8,
        locale="fr_CA",
    )
