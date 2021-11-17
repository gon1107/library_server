function getUrlParams() {
    var params = {};

    window.location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi,
        function(str, key, value) {
            params[key] = value;
        }
    );

    return params;
}

function searchBook(){
    let searchValue = document.getElementById('search-input').value.trim();
    if(searchValue.length > 1){
        location.href="/book/search/" + searchValue + "/";
    }
    else{
        alert('검색어('+ searchValue +')가 너무 짧습니다.');
    }
};

//window.addwindow.addEventListener('DOMContentLoaded', event => {
//id_stars

window.onload = function() {
    if (getUrlParams().error) {
        let div = document.createElement("div")
        div.append("slug가 빈 값입니다.")
        console.log(div.textContent)
    }

    document.getElementById('search-input').addEventListener('keyup', function(event){
    console.log(event.key)
    if(event.key === 'Enter'){
        searchBook();
        }
    });

    // 별점 버튼 애니메이션 처리
    if(document.getElementById('id_stars')){
        let stars = document.getElementById('id_stars').getElementsByClassName('star');

        for (let star of stars) {
            star.addEventListener('mouseover', function() {
                for (var i = 0; i < this.dataset.value; i++) {
                    stars[i].classList.add('star-hover');
                }
            });

            star.addEventListener('mouseout', function() {
                for (var i = 0; i < 5; i++) {
                    stars[i].classList.remove('star-hover');
                }

                let currentValue = document.getElementById('id_my_score').value;
                if (currentValue) {
                    for (var i = 0; i < currentValue; i++) {
                        stars[i].classList.add('star-hover');
                    }
                }
            });

            star.addEventListener('click', function(event) {
                event.preventDefault();
                document.getElementById('id_my_score').value = this.dataset.value;
            });
        }
    }

    let reviews = document.querySelectorAll('#review_stars');

    for (let review of reviews){
        let score = review.dataset.score
        console.log(score)
        let stars = review.getElementsByClassName('star');
        for (let star of stars){
            for (var i = 0; i < score; i++) {
                stars[i].classList.add('star-hover');
            }
        }
    }
}