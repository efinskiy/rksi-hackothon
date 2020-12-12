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
    priceAdd.innerHTML = `Добавить за ${price} р`;


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
        priceAdd.innerHTML = `Добавить за ${price} р`;
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
                        // footerButtonPrice.innerHTML = `${footerPrice} р`;
                        // let currentQ = quantity__footer.innerHTML.split('')[1];
                        // console.log(currentQ);
                        // footerQuantity.innerHTML = `x${Number(q)+Number(currentQ)}`;
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


closeBasket.onclick = () => {
    popupBasket.style.display = "none";
    buy__button.classList.toggle("active");
}

$("#buy__button").click(function () {
    popupBasket.style.display = "block";

    buy__button.classList.toggle("active");

    fetch("/api/getbasket", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            }
        }).then(response => response.json())
        .then(result => {
            console.log(result.response[2]);
            // console.log(JSON.stringify(result.response));
        });
});



histori.onclick = () =>{
    popupHistori.style.display = "block";
}
closeHistori.onclick = () =>{
    popupHistori.style.display = "none";
}
window.onload = (value) => {
    console.log(value);
}