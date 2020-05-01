var pieces = document.querySelectorAll("img");

for (var i = 0; i < pieces.length; ++i) {
    pieces[i].ondragstart = function() {
        return false;
    }
}

for (var i = 0; i < pieces.length; ++i) {
    pieces[i].onmousedown = function(event) {
        this.style.position = 'absolute';
        this.style.zIndex = 1000;
        document.body.append(this);
        moveAt(event.pageX, event.pageY);

        function moveAt(pageX, pageY) {
            this.style.left = pageX - this.offsetWidth / 2 + 'px';
            this.style.top = pageY - this.offsetHeight / 2 + 'px';
        }

        function onMouseMove(event) {
            moveAt(event.pageX, event.pageY);
        }

        document.addEventListener('mousemove', onMouseMove);

        this.onmouseup = function() {
            document.removeEventListener('mousemove', onMouseMove);
            this.onmouseup = null;
        };
    };
}