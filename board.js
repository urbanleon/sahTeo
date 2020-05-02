var pieces = document.querySelectorAll("img");

for (var i = 0; i < pieces.length; ++i) {
    pieces[i].ondragstart = function() {
        return false;
    }
}

var temp = null;
for (let i = 0; i < pieces.length; ++i) {
    pieces[i].onmousedown = function(event) {
        // this.style.position = 'absolute';
        // this.style.zIndex = 1000;
        document.body.append(this);
        
        moveAt(event.pageX, event.pageY, pieces[i]);

        function moveAt(pageX, pageY, obj) {
            obj.style.left = pageX - obj.offsetWidth / 2 + 'px';
            obj.style.top = pageY - obj.offsetHeight / 2 + 'px';
        }

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