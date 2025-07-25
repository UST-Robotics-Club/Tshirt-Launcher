var socket = io();

document.getElementById("speed1").addEventListener("input", function() {
	socket.emit("spin2", this.value)
});
document.getElementById("speed2").addEventListener("input", function() {
	socket.emit("spin1", this.value)
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
function onClick() {
  if(tilting) {
	  tilting = false;
	  window.removeEventListener('devicemotion', handleOrientation);
	  socket.emit("spin", 0)
	  return;
  } else{
	tilting = true;
  }
  
  if (typeof DeviceMotionEvent.requestPermission === 'function') {
	  alert("h")
    // Handle iOS 13+ devices.
    DeviceMotionEvent.requestPermission()
      .then((state) => {
        if (state === 'granted') {
          window.addEventListener('devicemotion', handleOrientation);
        } else {
          console.error('Request to access the orientation was rejected');
        }
      })
      .catch(console.error);
  } else {
	  	  alert("ff")

    // Handle regular non iOS 13+ devices.
    window.addEventListener('devicemotion', handleOrientation);
  }
}
document.getElementById("tiltMode").addEventListener("click", onClick)
