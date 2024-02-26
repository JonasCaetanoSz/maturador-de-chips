var phone = "@PHONE"

var newElment = document.createElement("a")
newElment.setAttribute("class", "_11JPr selectable-text copyable-texts OpenChat")
newElment.setAttribute("href", `http://wa.me/${phone}`)
newElment.setAttribute("title", `http://wa.me/${phone}`)
newElment.setAttribute("target", `_blank`)
document.body.append(newElment)
newElment.click()
newElment.remove()