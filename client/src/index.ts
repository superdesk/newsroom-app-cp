import {startApp} from 'newsroom-core/assets';
import {IArticle} from 'newsroom-core/assets/interfaces';


startApp().then((newshubApi) => {
    function getVersionsLabelText(item: IArticle, plural?: boolean): string {
        const {gettext} = newshubApi.localization;

        if (plural === true) {
            return item.extra?.type === 'transcript' ?
                gettext('segments') :
                gettext('versions');
        }

        return item.extra?.type === 'transcript' ?
            gettext('segment') :
            gettext('version');
    }

    newshubApi.ui.wire.getVersionsLabelText = getVersionsLabelText;
});
