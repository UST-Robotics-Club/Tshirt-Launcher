var socket = io();

function pointerEventHandlers(element, onDown, onUp) {
    element.addEventListener("pointerdown", function(e) {
        element.setPointerCapture(e.pointerId);
        return onDown(e);
    });
    element.addEventListener("pointerup", onUp);
    element.addEventListener("pointercancel", onUp);
}

function clamp(x, min, max) {
    return Math.min(max, Math.max(min, x));
}
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
let enableBtnLabel = document.getElementById("enable-label");
let disableBtnLabel = document.getElementById("disable-label");
let disableBtn = document.getElementById("disable");
let shootBtn = document.getElementById("shoot");
let forwardBtn = document.getElementById("forward");
let backwardBtn = document.getElementById("backward");
let leftBtn = document.getElementById("left");
let rightBtn = document.getElementById("right");
let tiltUpBtn = document.getElementById("tilt-up");
let tiltDownBtn = document.getElementById("tilt-down");
let rotateBtn = document.getElementById("rotate");
let holdTurretBtn = document.getElementById("hold");
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

disableBtnLabel.addEventListener("pointerdown", function (e) {
    e.preventDefault();
    socket.emit("disable");
    doPing();
});
enableBtnLabel.addEventListener("pointerdown", function (e) {
    e.preventDefault();
    socket.emit("enable");
    doPing();
});
holdTurretBtn.addEventListener("click", function (e){
    e.preventDefault();
    console.log("hold turrent event listener");
    socket.emit("hold");
});
pointerEventHandlers(shootBtn, function(e) {
    e.preventDefault();
    if (document.getElementById("shoot-safety").checked) {
        socket.emit("shoot", 0.1);
    }
}, function(e){
    e.preventDefault();
    if (document.getElementById("shoot-safety").checked) {
        socket.emit("shoot", 0.0);
    }
});
pointerEventHandlers(tiltUpBtn, function(e) {
    e.preventDefault();
    socket.emit("tiltUp");
}, function(e){
    e.preventDefault();
    socket.emit("stopTurret");
});
pointerEventHandlers(tiltDownBtn, function(e) {
    e.preventDefault();
    socket.emit("tiltDown");
}, function(e){
    e.preventDefault();
    socket.emit("stopTurret");
});
document.ondblclick = function(e) {
    e.preventDefault();
}

forwardBtn.addEventListener("mousedown", function (e) {
    e.preventDefault();
    socket.emit("forward");
});
backwardBtn.addEventListener("mousedown", function (e) {
    e.preventDefault();
    socket.emit("backward");
});
leftBtn.addEventListener("mousedown", function (e) {
    e.preventDefault();
    socket.emit("left");
});
rightBtn.addEventListener("mousedown", function (e) {
    e.preventDefault();
    socket.emit("right");
});
forwardBtn.addEventListener("mouseup", function (e) {
    e.preventDefault();
    socket.emit("stop");
});
backwardBtn.addEventListener("mouseup", function (e) {
    e.preventDefault();
    socket.emit("stop");
});
leftBtn.addEventListener("mouseup", function (e) {
    e.preventDefault();
    socket.emit("stop");
});
rightBtn.addEventListener("mouseup", function (e) {
    e.preventDefault();
    socket.emit("stop");
});
rotateBtn.addEventListener("mousedown", function (e) {
    e.preventDefault();
    socket.emit("rotateBarrels");
});

rotateBtn.addEventListener("mouseup", function (e) {
    e.preventDefault();
    socket.emit("stopTurret");
});

let joystickInner = document.getElementById("joystick-inner");
let joystickOuter = document.getElementById("joystick-outer");
let driveControlSection = document.getElementById("drive-controls");
let joystickId = false;
pointerEventHandlers(joystickInner, function(e) {
    e.preventDefault();
    joystickId = e.pointerId;
    let driveControlRect = driveControlSection.getBoundingClientRect();
    joystickInner.style.position = "absolute";
    joystickInner.style.left = -37 + driveControlRect.width / 2 + driveControlRect.left + "px";
    joystickInner.style.top = e.pageY - driveControlRect.top + "px";
}, function(e) {
    e.preventDefault();
    if (e.pointerId === joystickId) {
        joystickId = false;
        joystickInner.style.position = "relative";
        joystickInner.style.top = "60px";
        joystickInner.style.left = "60px";
        socket.emit("drive", 0, 0);
    }
});
document.addEventListener("pointermove", function(e) {
    if (e.pointerId === joystickId) {
        e.preventDefault();


        let fromRect = joystickOuter.getBoundingClientRect();
        let driveControlRect = driveControlSection.getBoundingClientRect();

        // Center of the outer element
        let cx = fromRect.left + fromRect.width / 2 + window.scrollX;
        let cy = fromRect.top + fromRect.height / 2 + window.scrollY;
        const maxDist = 75;
        let dy = e.pageY - cy;
        let dx = e.pageX - cx;

        dy = clamp(dy, -maxDist, maxDist);
        dx = clamp(dx, -0, 0);

        // Constrain to within maxDist px of the center
        innerJoystickCenterX = cx + dx;
        innerJoystickCenterY = cy + dy;

        joystickInner.style.left = innerJoystickCenterX - driveControlRect.left + "px";
        joystickInner.style.top = innerJoystickCenterY - driveControlRect.top + "px";

        let throttle = (document.getElementById("throttle").value / 100);
        socket.emit("drive", -Math.pow(dy / maxDist, 2) * throttle * Math.sign(dy), Math.pow(dx / maxDist, 2) * throttle * Math.sign(dx));
    }
});