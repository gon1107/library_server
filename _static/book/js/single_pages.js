window.onload = function() {
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
    }

//    let navbar_dropdown_menus = document.querySelectorAll('#navbarSupportedContent.nav-item dropdown.dropdown-item');
//    for (let menu of navbar_dropdown_menus ){
//        if(href == base_url + '/search/')
//                navbar_dropdown_menus [0].classList.add('active');
//        else if(href == base_url + '/book/')
//                navbar_dropdown_menus [1].classList.add('active');
//    }
}