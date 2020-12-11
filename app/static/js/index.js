'use strict';

let popup = document.querySelector(".popup"),
    closePopup = document.querySelector(".close");
// /api/getbalance
// {product_id: id}
const popupOpenFunction = (value) => {
    popup.style.display = "block";


    let name = value.childNodes[3].childNodes[1].childNodes[1].innerHTML;
    let price = Number(value.dataset.price);
    let onePiece = Number(value.dataset.price);
    let count = 1;
    let countProduct = popup.childNodes[1].childNodes[3].childNodes[1];
    let priceAdd = popup.childNodes[1].childNodes[3].childNodes[5].childNodes[1];
    let countMax = 0;


    popup.childNodes[1].childNodes[1].childNodes[1].innerHTML = name;

    countProduct.innerHTML = `Желаемое количество: ${count}`;
    priceAdd.innerHTML = `Добавить за ${price} р`;

    closePopup.onclick = () => {
        popup.style.display = "none";
    }

    minus.onclick = () => {
        if (count - 1 == 0) {
            alert('количество должно положительным');
            console.log(count);
            return;
        } else {
            count--;
            price = price - onePiece;
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
        }
        countProduct.innerHTML = `Желаемое количество: ${count}`;
        priceAdd.innerHTML = `Добавить за ${price} р`;
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
        .then(result => countMax=JSON.stringify(result.q))
        console.log(countMax);

}