function turnCamera(dir=0){
    $.ajax({
        type: "POST",
        url: "/camera_turn",
        data: {"value": dir},
    })
}

function focusCamera(){
    $.ajax({
        type: "POST",
        url: "/camera_focus",
        data: "",
    })
}

var webrtc = new SimpleWebRTC({
    url: '/',
    media: { audio: true, video: false },
    receiveOnly: true
});

webrtc.on('readyToCall', function() {
    webrtc.joinRoom('audio');
});

webrtc.on('stream', function(stream) {
    document.getElementById('audio').srcObject = stream;
});


