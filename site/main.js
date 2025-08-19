var socket = io();

document.getElementById("speed1").addEventListener("input", function () {
    socket.emit("spin2", parseFloat(this.value) / 10.0)
});
document.getElementById("speed2").addEventListener("input", function () {
    socket.emit("spin1", parseFloat(this.value) / 10.0)
});
function stop() {
    socket.emit("spin1", 0);
    socket.emit("spin2", 0);

    document.getElementById("speed1").value = 0;
    document.getElementById("speed2").value = 0;

}
window.addEventListener("touchend", stop);
window.addEventListener("mouseup", stop);
window.addEventListener("touchcancel", stop);
let tilting = false;
function handleOrientation(event) {
    const alpha = event.alpha;
    const beta = event.beta;
    const gamma = event.gamma;
    let val = Math.max(Math.min(100, beta), -100)
    socket.emit("spin", val);
}
let enableBtn = document.getElementById("enable");
let disableBtn = document.getElementById("disable");
let pingHistory = [];
function doPing() {
    let start = Date.now();
    socket.emit("ping", function (enabled) {
        let now = Date.now()
        pingHistory.unshift(now - start);
        pingHistory = pingHistory.slice(0, 6);
        document.getElementById("ping").innerHTML = pingHistory.join("<br>");
        if (enabled) {
            enableBtn.checked = true;
            disableBtn.checked = false;
            document.body.classList.add("control-enabled");
        } else {
            disableBtn.checked = true;
            enableBtn.checked = false;
            document.body.classList.remove("control-enabled");

        }
    })
}
setInterval(doPing, 750);

disableBtn.addEventListener("click", function (e) {
    e.preventDefault()
    socket.emit("disable");
    doPing();
});
enableBtn.addEventListener("click", function (e) {
    e.preventDefault();
    socket.emit("enable");
    doPing();
});