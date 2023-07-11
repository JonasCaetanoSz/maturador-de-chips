var MenuDiv = document.querySelector('[data-testid="conversation-menu-button"]')
var MenuButton = MenuDiv.querySelector('[data-testid="menu"]')
MenuButton.click()

// atraso de 500 mlisegundos para que o js na pagina reconheça o evento e libere o botão de fechar conversa

setTimeout(() => {
    let CloseButton = document.querySelector('[aria-label="Fechar conversa"]')
    CloseButton.click()
}, 500);