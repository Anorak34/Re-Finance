document.addEventListener('DOMContentLoaded', function() {
    let elements = document.getElementsByClassName('cash');
    for (let i = 0; i < elements.length; i++)
    {
        let user_currency = elements[i].dataset.currency;
        let value = parseFloat(elements[i].innerHTML);
        value = Intl.NumberFormat('en-US', { style: 'currency', currency: user_currency }).format(value);
        elements[i].innerHTML = value;
    }
});