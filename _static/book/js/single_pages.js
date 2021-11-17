window.addEventListener('DOMContentLoaded', event => {
    // Fixed-top function
    var fixedTop = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('fixed-top')
        } else {
            navbarCollapsible.classList.add('fixed-top')
        }

    };

    // fixed-top
    fixedTop();

    // fixed-top when page is scrolled
    document.addEventListener('scroll', fixedTop);

    let navbar_menus = document.getElementById('navbarSupportedContent').getElementsByClassName('nav-item');
    let href = document.location.href;

    let base_url = href.split('/')[0]+ '//' + href.split('/')[2]
    for (let menu of navbar_menus){
        if(href == base_url + '/')
            navbar_menus[0].classList.add('active');
        else if(href == base_url + '/info/')
            navbar_menus[1].classList.add('active');
        else if(href == base_url + '/book/reservation_list/')
            navbar_menus[2].classList.add('active');
        else if(href == base_url + '/book/' || href == base_url + '/search/' || href.includes(base_url + '/book/search/'))//href.indexOf(base_url + '/book/search/') != -1
            navbar_menus[navbar_menus.length-1].classList.add('active');
    }
});
