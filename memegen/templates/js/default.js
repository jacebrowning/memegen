function getCookie(c_name)
{
    // From http://www.w3schools.com/js/js_cookies.asp
    var c_value = document.cookie;
    var c_start = c_value.indexOf(" " + c_name + "=");
    if (c_start == -1) {
        c_start = c_value.indexOf(c_name + "=");
    }
    if (c_start == -1) {
        c_value = null;
    } else {
        c_start = c_value.indexOf("=", c_start) + 1;
        var c_end = c_value.indexOf(";", c_start);
        if (c_end == -1) {
            c_end = c_value.length;
        }
        c_value = unescape(c_value.substring(c_start,c_end));
    }
    return c_value;
}

// JSON highlighting.
prettyPrint();

// Bootstrap tooltips.
$('.js-tooltip').tooltip({
    delay: 1000
});

// Deal with rounded tab styling after tab clicks.
$('a[data-toggle="tab"]:first').on('shown', function (e) {
    $(e.target).parents('.tabbable').addClass('first-tab-active');
});
$('a[data-toggle="tab"]:not(:first)').on('shown', function (e) {
    $(e.target).parents('.tabbable').removeClass('first-tab-active');
});

$('a[data-toggle="tab"]').click(function(){
    document.cookie="tabstyle=" + this.name + "; path=/";
});

// Store tab preference in cookies & display appropriate tab on load.
var selectedTab = null;
var selectedTabName = getCookie('tabstyle');

if (selectedTabName) {
    selectedTab = $('.form-switcher a[name=' + selectedTabName + ']');
}

if (selectedTab && selectedTab.length > 0) {
    // Display whichever tab is selected.
    selectedTab.tab('show');
} else {
    // If no tab selected, display rightmost tab.
    $('.form-switcher a:first').tab('show');
}

// Google Analytics
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
ga('create', '{{ ga_tid }}', 'auto');
ga('send', 'pageview');
