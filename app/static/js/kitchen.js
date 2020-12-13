// socket = io.connect('/sockets/kitchen');

// socket.on('connect', function(){
//     socket.emit('joined', {});
// });
// socket.on('message',function(data){
//     console.log(data)
// });
$(document).ready(function () {
    socket = io.connect(`http://${document.domain}:${location.port}/sockets/kitchen`);

    socket.on('connect', function () {
        socket.emit('joined', {});
    });
    socket.on('message', function (data) {
        console.log(data)
    });
})