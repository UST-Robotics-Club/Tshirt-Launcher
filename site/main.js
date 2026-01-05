var socket = io();
function pointerEventHandlers(element, onDown, onUp) {
    element.addEventListener("pointerdown", function (e) {
        element.setPointerCapture(e.pointerId);
        return onDown(e);
    });
    element.addEventListener("pointerup", onUp);
    element.addEventListener("pointercancel", onUp);
}

function clamp(x, min, max) {
    return Math.min(max, Math.max(min, x));
}


let enableBtn = document.getElementById("enable");
let unstableSwitch = document.getElementById("unstable-switch");
let enableBtnLabel = document.getElementById("enable-label");
let disableBtnLabel = document.getElementById("disable-label");
let disableBtn = document.getElementById("disable");
let shootBtn = document.getElementById("shoot");
let leftBtn = document.getElementById("turret-left");
let rightBtn = document.getElementById("turret-right");
let tiltUpBtn = document.getElementById("tilt-up");
let tiltDownBtn = document.getElementById("tilt-down");
let rotateBtn = document.getElementById("rotate");
let lockOn = document.getElementById("lock-on");
let saveButton = document.getElementById("save-settings");
let valveTime = document.getElementById("valve-time");
let modeSelect = document.getElementById("mode-select");
let pingHistory = [];
let timeOffset = Number.MAX_SAFE_INTEGER;
function getForeignTime() {
    // get the time according to the robot
    return (Date.now() + timeOffset) / 1000;
}
function isUnstable() {
    return unstableSwitch.checked;
}
function doPing() {
    let start = Date.now();
    socket.emit("ping", function (status) {
        let enabled = status[1][0];
        let serverTime = status[1][1] * 1000;
        unstableSwitch.checked = status[1][2];
        let now = Date.now();
        let thisPing = now - start;
        let timeDiff = serverTime - start;
        if(Math.abs(timeDiff) < Math.abs(timeOffset)) {
            // Lowest time diff is probably most accurate
            timeOffset = timeDiff;
        }
        let amDriving = status[0].includes(socket.id);
        pingHistory.unshift(thisPing);
        pingHistory = pingHistory.slice(0, 6);
        document.getElementById("ping").innerHTML = pingHistory.join("<br>");
        if (enabled) {
            enableBtn.checked = true;
            disableBtn.checked = false;
            if (amDriving) {
                document.body.classList.add("control-enabled");
                document.body.classList.remove("enabled-not-driving");
            } else {
                document.body.classList.add("enabled-not-driving");
                document.body.classList.remove("control-enabled");
            }
        } else {
            disableBtn.checked = true;
            enableBtn.checked = false;
            document.body.classList.remove("control-enabled");
            document.body.classList.remove("control-enabled");
            document.body.classList.remove("enabled-not-driving");

        }
    })
}
let waitingForFrame = false;
let lastFrameTime = 0;
function getCameraFrame() {
    if (waitingForFrame) return; // prevent multiple frame getting loops
    waitingForFrame = true;
    socket.emit("frame", function (data) {
        waitingForFrame = false;
        const mimeType = 'image/jpeg';
        const blob = new Blob([data], { type: mimeType });
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById("camera").src = imageUrl;
        setTimeout(getCameraFrame, 16);
        lastFrameTime = Date.now();
    });
}
setInterval(function () {
    if (waitingForFrame && (Date.now() - lastFrameTime) > 3000) {
        waitingForFrame = false;
        getCameraFrame();
    }
}, 3000);
setInterval(doPing, 100);
getCameraFrame();

let periodicSends = {};
function sendInput(category, message, ...values) {
    socket.emit(message, ...[...values, getForeignTime()]);
    if(isUnstable()) {
        periodicSends[category] = [message, values];
    }
}
function clearInput(category) {
    delete periodicSends[category];
}
setInterval(function () {
    // This resends inputs during unstable mode to confirm continued input
    // If the robot doesn't receive something after 150ms, it will slow down over 100ms.
    if (isUnstable()) {
        for(let cat in periodicSends) {
            let entry = periodicSends[cat];
            socket.emit(entry[0], ...[...entry[1], getForeignTime()]);
        }
    }
}, 100);

socket.on("connect", function () {
    document.getElementById("control-card").classList.remove("disconnected");
});
socket.on("disconnect", function () {
    document.getElementById("control-card").classList.add("disconnected");
});
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
unstableSwitch.addEventListener("change", function (e) {
    e.preventDefault();
    socket.emit("setUnstableMode", isUnstable());
    periodicSends = {};
});

// pointerEventHandlers(shootBtn, function(e) {
//     e.preventDefault();
//     if (document.getElementById("shoot-safety").checked) {
//         socket.emit("shoot", 0.1);
//     }
// }, function(e){
//     e.preventDefault();
//     socket.emit("shoot", 0.0);
// });
pointerEventHandlers(shootBtn, function (e) {
    e.preventDefault();
    if (document.getElementById("shoot-safety").checked) {
        sendInput("shoot", "autoshoot", true);
    }
}, function (e) {
    e.preventDefault();
    sendInput("shoot", "autoshoot", false);
    clearInput("shoot");
});
pointerEventHandlers(tiltUpBtn, function (e) {
    e.preventDefault();
    sendInput("tilt", "tiltUp");
}, function (e) {
    e.preventDefault();
    sendInput("tilt", "stopTilt");
    clearInput("tilt");
});
pointerEventHandlers(tiltDownBtn, function (e) {
    e.preventDefault();
    sendInput("tilt", "tiltDown");
}, function (e) {
    e.preventDefault();
    sendInput("tilt", "stopTilt");
    clearInput("tilt");
});
pointerEventHandlers(leftBtn, function (e) {
    e.preventDefault();
    sendInput("pivot", "turretLeft");
}, function (e) {
    e.preventDefault();
    sendInput("pivot", "stopPivot");
    clearInput("pivot");
});
pointerEventHandlers(rightBtn, function (e) {
    e.preventDefault();
    sendInput("pivot", "turretRight");
}, function (e) {
    e.preventDefault();
    sendInput("pivot", "stopPivot");
    clearInput("pivot");
});
pointerEventHandlers(rotateBtn, function (e) {
    e.preventDefault();
    sendInput("geneva", "manualGeneva", 0.1);
}, function (e) {
    e.preventDefault();
    sendInput("geneva", "manualGeneva", 0);
    clearInput("geneva");
});
pointerEventHandlers(lockOn, function (e) {
    e.preventDefault();
    socket.emit("setAuto", "center");
}, function (e) {
    e.preventDefault();
    socket.emit("setAuto", "none");
});
pointerEventHandlers(saveButton, function (e) {
    e.preventDefault();
    socket.emit("setValveTime", parseFloat(valveTime.value));
}, function (e) {
    e.preventDefault();
});

document.ondblclick = function (e) {
    e.preventDefault();
}
modeSelect.addEventListener("change", function (e) {
    document.body.classList.remove("show-1", "show-2", "show-3");
    document.body.classList.add("show-" + this.value);
    sendInput("drive", "drive", 0, 0);
    periodicSends = {};
    if(this.value == "3") {
        socket.emit("getValveTime", function(t) {
            valveTime.value = t;
        });
    }
});

let joystickInner = document.getElementById("joystick-inner");
let joystickOuter = document.getElementById("joystick-outer");
let forwardStick = document.getElementById("forward-stick");
let rotateStick = document.getElementById("rotate-stick");
let driveControlSection = document.getElementById("drive-controls");
let joystickId = false;
let currDriveRot = 0;
let currDriveForward = 0;
pointerEventHandlers(joystickInner, function (e) {
    e.preventDefault();
    joystickId = e.pointerId;
    let driveControlRect = driveControlSection.getBoundingClientRect();
    joystickInner.style.position = "absolute";
    joystickInner.style.left = -37 + driveControlRect.width / 2 + driveControlRect.left + "px";
    joystickInner.style.top = e.pageY - driveControlRect.top + "px";
}, function (e) {
    e.preventDefault();
    if (e.pointerId === joystickId) {
        joystickId = false;
        joystickInner.style.position = "relative";
        joystickInner.style.top = "60px";
        joystickInner.style.left = "60px";
        sendInput("drive", "drive", 0, 0);
        clearInput("drive");
    }
});
pointerEventHandlers(forwardStick, function (e) {
    forwardStick.classList.add("stick-active");
}, function (e) {
    forwardStick.value = 0;
    updateTwoSliderDriving();
    forwardStick.classList.remove("stick-active");
});
pointerEventHandlers(rotateStick, function (e) {
    rotateStick.classList.add("stick-active");
}, function (e) {
    rotateStick.value = 0;
    updateTwoSliderDriving();
    forwardStick.classList.remove("stick-active");
});
function updateTwoSliderDriving() {
    let throttle = (document.getElementById("throttle").value / 100);
    let turnThrottle = Math.min(throttle, 0.25);
    let forward = forwardStick.value / 100 * throttle;
    let rotate = rotateStick.value / 100 * turnThrottle;
    sendInput("drive", "drive", forward, rotate);
    if(rotate === 0 && forward === 0) {
        clearInput("drive");
    }
}
forwardStick.addEventListener("input", function () {
    updateTwoSliderDriving();
});
rotateStick.addEventListener("input", function () {
    updateTwoSliderDriving();
});
document.addEventListener("pointermove", function (e) {
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
        dx = clamp(dx, -maxDist, maxDist);

        innerJoystickCenterX = cx + dx;
        innerJoystickCenterY = cy + dy;

        joystickInner.style.left = innerJoystickCenterX - driveControlRect.left + "px";
        joystickInner.style.top = innerJoystickCenterY - driveControlRect.top + "px";

        let throttle = (document.getElementById("throttle").value / 100);
        // Square the inputs so we can get finer control without losing highest speed
        currDriveForward = -Math.pow(dy / maxDist, 2) * throttle * Math.sign(dy);
        currDriveRot = Math.pow(dx / maxDist, 2) * throttle * Math.sign(dx);
        sendInput("drive", "drive", currDriveForward, currDriveRot);
    }
});