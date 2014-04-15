hljs.configure({tabReplace: "    "});
hljs.initHighlightingOnLoad();

// get sidebar and store top position
var sidebar = $("nav");
var sidebar_top = sidebar.position().top;

$(window).scroll(function() {
    var scroll_top = $(window).scrollTop();

    if (scroll_top <= sidebar_top){
        sidebar.removeClass("sticky");
    } else if (scroll_top >= sidebar_top) {
        sidebar.addClass("sticky");
    }   
});


/* nicer scrolling (slightly offset) */
var scroll_to_hash = function() {
    var el = document.getElementById(window.location.hash.substring(1));

    if (el) {
        $("html, body").scrollTop($(el).offset().top - 35);
    }
}

var $root = $("html, body");
$("a[href*=#]").click(function() {
    window.location.hash = this.hash;
    scroll_to_hash();
    return false;
});

$(function() {
    scroll_to_hash();
});