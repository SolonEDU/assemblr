$(window).on('load', () => {
    let mylanguages = []
    $("#addlanguage").click(() => {
        let language = $("#languageselect option:selected")
        let color = language.val()
        let languageid = language.attr('id')
        if (color.length > 0 && !(mylanguages.includes(languageid))) {
            mylanguages.push(languageid);
            $("#mylanguages").append(
                `<div class="col-sm-6 col-md-4 col-lg-3 py-2 custom-control custom-checkbox">
                    <input type="checkbox" name="language" class="custom-control-input" value="${languageid}" id="${languageid}" checked>
                    <label class="custom-control-label" for="${languageid}">
                        <span class="dot" style="background-color: ${color}"></span>
                        ${languageid}
                    </label>
                    <input type="hidden" name="${languageid}" value="${color}">
                </div>`
            );
        }
    });
});