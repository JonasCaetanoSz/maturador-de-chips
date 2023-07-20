var ElementReference = document.getElementById("pane-side")
var phone = "@PHONE"

if (ElementReference === null){

    let xhr = new XMLHttpRequest()
    xhr.open("GET", `/maturador/api/account-blocked/{"phone":"${phone}"}`, true)
    xhr.send()
}