'use strict';

let popup = document.querySelector(".popup"),
    closePopup = document.querySelector(".close");
let footerPrice = 0;
const popupOpenFunction = (value) => {
    popup.style.display = "block";


    let name = value.childNodes[3].childNodes[1].childNodes[1].innerHTML;
    let price = Number(value.dataset.price);
    let onePiece = Number(value.dataset.price);
    let count = 1;
    let countProduct = popup.childNodes[1].childNodes[3].childNodes[1];
    let priceAdd = popup.childNodes[1].childNodes[3].childNodes[5].childNodes[1];
    let countMax = 0;


    // footer button
    let footerButtonPrice = buy__button.childNodes[1].childNodes[1];
    // console.log(footerButtonPrice);

    popup.childNodes[1].childNodes[1].childNodes[1].innerHTML = name;

    countProduct.innerHTML = `Желаемое количество: ${count}`;
    priceAdd.innerHTML = `Добавить за ${price} р`;

    closePopup.onclick = () => {
        popup.style.display = "none";
    }

    minus.onclick = () => {
        if (count - 1 == 0) {
            alert('количество должно положительным');
            return;
        } else {
            count--;
            price = price - onePiece;
            // footerPrice = footerPrice-price;
        }
        countProduct.innerHTML = `Желаемое количество: ${count}`;
        priceAdd.innerHTML = `Добавить за ${price} р`;
        // footerButtonPrice.innerHTML = `${footerPrice} р`;
    }
    plus.onclick = () => {
        if (count + 1 > countMax) {
            alert(`В столовой осталось лишь ${countMax}`);
            return;
        } else {
            count++;
            price = price + onePiece;
            // footerPrice = footerPrice+price;
        }
        countProduct.innerHTML = `Желаемое количество: ${count}`;
        priceAdd.innerHTML = `Добавить за ${price} р`;
        // footerButtonPrice.innerHTML = `${footerPrice} р`;
    }

    priceAdd.onclick = () =>{
        // alert(1);
        footerPrice = price;
        footerButtonPrice.innerHTML = `${footerPrice} р`;
        popup.style.display = "none";
    }
    // POST

    let id = value.dataset.id;
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
}

