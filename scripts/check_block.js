var ChatList = document.querySelector('[aria-label="Lista de conversas"]')
var phone = "@PHONE"

if (ChatList == null){

    let xhr = new XMLHttpRequest()
    xhr.open("GET", `/maturador/api/account-blocked/{"phone":"${phone}"}`, true)
    xhr.send()
}