// atualizar o status da aquecimento

setInterval(() => {
    const notifications = controller.long_polling().then(notifications => {
    notifications = JSON.parse(notifications);
    notifications.forEach( notification => {
        
        var SendOf = notification.enviadoDe;
        var ReceivedBy = notification.recebidoPor;
        var message = notification.mensagem;
        var hours = notification.horario; //new Date().toLocaleDateString();


        var newRow = $("<tr>");
        var cols = "";
        cols += "<td>" + SendOf + "</td>";
        cols += "<td>" + ReceivedBy + "</td>";
        cols += "<td class='messageTd'>" + `<input value="${message}" class="messageInput" </input>` + "</td>";
        cols += "<td>" + hours + "</td>";
        newRow.append(cols);
        $("#logTableBody").append(newRow);

        // faz o scroll automático na tabela de logs

        var logTableContainer = document.getElementsByClassName("log-table-container")[0];
        logTableContainer.scrollTop = logTableContainer.scrollHeight;

    })}); 1 * 1000
})

// parar o aquecimento

document.querySelector(".btn-danger").addEventListener("click", (el)=> {
    el.target.disabled = true;
    controller.stop_maturation();
})