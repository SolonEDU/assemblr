const label = "assemblr_";
var i = 0;

$(window).on('load', () => {
    var assemble = setInterval(() => {
        $("#label").append(label[i++]);
        if (i == label.length) {
            clearInterval(assemble);
            var flicker = setInterval(() => {
                $("#flicker").css("visibility", "hidden");
                setTimeout(() => {
                    $("#flicker").css("visibility", "visible");
                    i++;
                }, 500);
                if (i == 16) {
                    clearInterval(flicker);
                    setTimeout(() => {
                        $("#flicker").css("display", "none")
                    }, 500);
                }
            }, 1000)
        }
    }, 200)
});
