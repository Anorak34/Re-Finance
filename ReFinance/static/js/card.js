var cards = [{
    name: "unknown",
    color: "#363636",
    src: ""
  }, {
    name: "mastercard",
    color: "#31ad9b",
    src: "https://upload.wikimedia.org/wikipedia/commons/0/04/Mastercard-logo.png"
  }, {
    name: "visa",
    color: "#d92525",
    src: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Visa_Inc._logo.svg/2000px-Visa_Inc._logo.svg.png"
  }, {
    name: "americanExpress",
    color: "#015694",
    src: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/American_Express_logo.svg/600px-American_Express_logo.svg.png"
  }];

let number_input = document.getElementById("number");
let month_input = document.getElementById("month");
let year_input = document.getElementById("year");
let name_input = document.getElementById("name");

let card_number_elem = document.getElementById("card_number");
let date_value_elem = document.getElementById("date_value");
let fullname_elem = document.getElementById("fullname");

let bank_img = document.getElementById("bankid");
let root = document.documentElement;
let selected_card = 0;

function handleNumber(){
    let card_number = number_input.value;
    let formatted_card_number = '';
    if (card_number.length == 0) {
        card_number_elem.innerHTML = '&#x25CF;&#x25CF;&#x25CF;&#x25CF; &#x25CF;&#x25CF;&#x25CF;&#x25CF; &#x25CF;&#x25CF;&#x25CF;&#x25CF; &#x25CF;&#x25CF;&#x25CF;&#x25CF; ';
        selected_card = 0;
    }
    else {
        for (let i = 0; i < card_number.length; i++){
            if (i == 4 || i == 9 || i == 14) {
                if (card_number[i] != ' ') {
                    formatted_card_number += ' ';
                }
            }
            formatted_card_number += card_number[i];
        }
        number_input.value = formatted_card_number;
        card_number_elem.innerHTML = formatted_card_number;

        if(parseInt(formatted_card_number.substring(0, 2)) > 50 && parseInt(formatted_card_number.substring(0, 2)) < 56) {
            selected_card = 1;
        }
        else if(parseInt(formatted_card_number.substring(0, 1)) == 4) {
            selected_card = 2;  
        }
        else if(parseInt(formatted_card_number.substring(0, 2)) == 34 || parseInt(formatted_card_number.substring(0, 2)) == 37) {
            selected_card = 3; 
        }
        else {
            selected_card = 0; 
        }
    }
    root.setAttribute("style", "--card-color: " + cards[selected_card].color);
    bank_img.setAttribute("src", cards[selected_card].src);
};

function handleDate(){
    month = month_input.value;
    if (month < 10) {
        month = '0' + month;
    }
    date_value_elem.innerHTML = month + ' / ' + year_input.value;
};

function handleName(){
    let name = name_input.value;
    if (name.length > 0) {
        fullname_elem.innerHTML = name;
    }
    else {
        fullname_elem.innerHTML = 'FULL NAME';
    }
};