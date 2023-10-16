var MenuDiv = document.querySelectorAll('[title="Mais opções"]')[1]

var MenuButton = MenuDiv.querySelector('[data-icon="menu"]')
MenuButton.click()

// atraso de 500 mlisegundos para que o js na pagina reconheça o evento e libere o botão de fechar conversa

setTimeout(() => {
    let CloseButton = document.querySelector('[aria-label="Fechar conversa"]')
    CloseButton.click()
}, 500);