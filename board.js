var pieces = document.querySelectorAll("img");
var squares = document.querySelectorAll("div");

for (let i = 0; i < pieces.length; ++i) {  

    //disable native drag event
    pieces[i].ondragstart = function() {
        return false;
    }

    //create event handlers for custom drag events
    pieces[i].onmousedown = function(event) {
        this.style.position = 'absolute';
        this.style.zIndex = 1000;
        document.body.append(this);
        
        moveAt(event.pageX, event.pageY, pieces[i]);

        function onMouseMove(event) {
            moveAt(event.pageX, event.pageY, pieces[i]);
        }
        
        document.addEventListener('mousemove', onMouseMove);

        pieces[i].onmouseup = function() {
            document.removeEventListener('mousemove', onMouseMove);
            this.onmouseup = null;
        };
    };
}

function moveAt(pageX, pageY, obj) {
    obj.style.left = pageX - obj.offsetWidth / 2 + 'px';
    obj.style.top = pageY - obj.offsetHeight / 2 + 'px';
}