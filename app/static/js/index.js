'use strict';

let popup = document.querySelector(".popupSelected"),
    popupBasket = document.querySelector(".popupBasket"),
    popupHistori =document.querySelector(".popupHistori"),
    closePopup = document.querySelector(".close");
let footerPrice = 0;
let footerQ = 0;

const popupOpenFunction = (value) => {
    popup.style.display = "block";
    footer__menu.classList.toggle("active");

    let name = value.childNodes[3].childNodes[1].childNodes[1].innerHTML;
    let price = Number(value.dataset.price);
    let onePiece = Number(value.dataset.price);
    let count = 1;
    let countProduct = popup.childNodes[1].childNodes[3].childNodes[1];
    let priceAdd = popup.childNodes[1].childNodes[3].childNodes[5].childNodes[1];
    let countMax = 0;
    let id = value.dataset.id;
    // footer button
    let footerButtonPrice = buy__button.childNodes[1].childNodes[1];
    let footerQuantity = buy__button.childNodes[1].childNodes[3].childNodes[1];
    popup.childNodes[1].childNodes[1].childNodes[1].innerHTML = name;

    countProduct.innerHTML = `Желаемое количество: ${count}`;
    priceAdd.innerHTML = `Добавить за ${price}  ₽`;


    closePopup.onclick = () => {
        footer__menu.classList.toggle("active");
        popup.style.display = "none";
    }

    minus.onclick = () => {
        if (count - 1 == 0) {
            alert('количество должно положительным');
            return;
        } else {
            count--;
            price = price - onePiece;
            footerQ = count;
        }
        countProduct.innerHTML = `Желаемое количество: ${count}`;
        priceAdd.innerHTML = `Добавить за ${price}  ₽`;
    }


    plus.onclick = () => {
        if (count + 1 > countMax) {
            alert(`В столовой осталось лишь ${countMax}`);
            return;
        } else {
            count++;
            price = price + onePiece;
            footerQ = count;
        }
        countProduct.innerHTML = `Желаемое количество: ${count}`;
        priceAdd.innerHTML = `Добавить за ${price} р`;
    }
    fetch("/api/getbalance", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify({
                "product_id": id
            })
        }).then(response => response.json())
        .then(result => JSON.stringify(result.q)).then(res => {
            countMax = res;
        });


    priceAdd.onclick = () => {
        const addtoBasket = (basket) => {
            fetch("/api/addtobasket", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json;charset=utf-8'
                    },
                    body: JSON.stringify(basket)
                }).then(response => response.json())
                .then(result => {
                    let status = result.status;
                    let q = JSON.stringify(result.q);
                    footerQ = q + count;
                    if (status == "good") {
                        location.reload();
                    }
                    if (status == "bad") {
                        alert("Количество товара превышенно");
                    }
                });
        }
        countMax -= count;
        footerPrice += price;

        popup.style.display = "none";
        // addBasket(id,count);
        let basket = {
            "item_id": id,
            "amount": count
        }
        // добовление в корзину
        addtoBasket(basket);

    }
}
footer__menu.onclick = () =>{
    popupBasket.style.display = "none";
    popupHistori.style.display = "none";
    buy__button.classList.remove("active");
    histori.classList.remove("active");
    footer__menu.classList.add("active");
}

$("#closeBasket").click(function () {
    popupBasket.style.display = "none";
    popupHistori.style.display = "none";
    buy__button.classList.remove("active");
    histori.classList.remove("active");
    footer__menu.classList.add("active");
})

$("#buy__button").click(function () {
    popupBasket.style.display = "block";
    popupHistori.style.display = "none";
    $("#popupBasket__body").empty();
    $( "#histori" ).removeClass( "active");
    $( "#footer__menu" ).removeClass( "active");
    // addClass
    $( "#buy__button" ).addClass( "active");

    fetch("/api/getbasket", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            }
        }).then(response => response.json())
        .then(result => {
            let arrItems = result.response.items;
            let itemsBasket={
                item:[],
                name:[],
                amount:[],
                value:[]
            };

            for (const key in arrItems) {
                itemsBasket.item.push(arrItems[key].id);
                itemsBasket.name.push(arrItems[key].name);
                itemsBasket.amount.push(arrItems[key].amount);
                itemsBasket.value.push(arrItems[key].value);
            }
            console.log(itemsBasket);
            for (let i = 0; i < itemsBasket.item.length; i++) {
                $("#popupBasket__body").append(`<div class="popup-body__position">
                <p class="position__name"><b>${itemsBasket.name[i]}</b></p>
                <div class="position__name__counter">
                    <p class="count_pos"><i>Количество <b>${itemsBasket.amount[i]} шт</b></i></p>
                    <p class="price"><i>Стоймость <b>${itemsBasket.value[i]}  ₽</b></i></p>
                </div>
                <hr class="popupBasket__hr">
            </div>`);
            }
            $("#popupBasket__body").append(`<p class="summ"> Итого <b>${result.summ} ₽</b></p>`);
            $("#popupBasket__body").append(`<div class="popup-body__button_add button " onclick="hendelBuy()">
            <p class="button_text_add">Оплатить</p>
        </div>`);
        });
});

const hendelBuy = ()=>{
    // /api/getpayurl

    fetch("/api/getpayurl", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
    }).then(response => JSON.stringify(response))
    .then(result => {
       
    });
}

histori.onclick = () =>{
    popupHistori.style.display = "block";
    popupBasket.style.display = "none";
    histori.classList.add("active");
    buy__button.classList.remove("active");
    footer__menu.classList.remove("active");
}
closeHistori.onclick = () =>{
    popupHistori.style.display = "none";
}
function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
      "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
  }


window.onload = (dbg) => {
   
    console.log(getCookie("policy"));
    if (getCookie("policy") == undefined) {
        $(".cookie__block").show();
    }else{
        $(".cookie__block").hide();
    }
}
$(".cookie__close").click(function () {
    $(".cookie__block").hide();
    fetch("/api/setpolicy", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
    }).then(response => response)
    .then(result => {
        console.log(result);
    });
})