var message = "@MESSAGE"

// execCommand está está obsoleta, mas parece não haver um substituto pra ela. leia mais sobre em: 
//https://stackoverflow.com/questions/60581285/execcommand-is-now-obsolete-whats-the-alternative

document.execCommand('insertText', false, message)

// atraso de 500 milisegundos para que o whatssap reconheça o evento e libere o botão de enviar

setTimeout(() => {
    let SendButton = document.querySelector('[data-icon="send"]')
    SendButton.click();
}, 500);