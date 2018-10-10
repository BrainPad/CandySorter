nextWithTimeout = (nextFunc, timeout) => {
    console.log("Setting paused to false and starting duration")
    var paused = false;

    var timeout = setTimeout(function() {
        window.document.onkeyup = null;
        nextFunc()
    }, timeout);

    window.document.onkeyup = (event) => {
        console.log("Key pressed")
        if (event.which === 32) {
            if (paused) {
                $(".pauseIcon img").replaceWith("<img src='/static/images/pauseicon.png'/>")
                console.log("Resuming after pause");
                window.document.onkeyup = null;
                nextFunc();
            } else {
                console.log("Clearing duration and pausing")
                clearTimeout(timeout);
                paused = true;
                $(".pauseIcon img").replaceWith("<img src='/static/images/fwdicon.png'/>");
            }
        }
    };
}

class TimeoutManager {
    constructor() {
        // Function to be called on next or when the timer expires
        this.nextFunc = null;
        // The time before the timeout expires
        this.duration = null;
        // The timeout object so that the timeout can be cancelled
        this.timeout = null;

        // Flag to indicate if we can pause
        this.canStop = false;
        // Flag to indicate that the timeout is active
        this.stopped = false;

        this.initEventHandlers()
    }

    startTimer(nextFunc, duration) {
        this.nextFunc = nextFunc;
        this.duration = duration;
        this.timeout = setTimeout(this.onContinue.bind(this), this.duration)

        this.canStop = true;
        this.stopped = false;

        this.showCountdown();
    }

    initEventHandlers() {
        window.document.onkeyup = (event) => {
            console.log("Key pressed", event.code)
            switch (event.code) {
                case "Space":
                    this.onSpacePressed();
                    break;
                case "PageUp":
                    this.onStop();
                    break;
                case "PageDown":
                    this.onContinue()
                    break;
            }
        };
    }

    showCountdown() {
        $(".pauseIcon img").replaceWith("<img src='/static/images/pauseicon.png'/>")

        var svg = d3.select(".progress");
        svg.selectAll("circle").remove();
        svg.append("circle")
            .attr("r", "17.5")
            .attr("cx", 20).attr("cy", 20)
            .attr("class", "progress_value")
            .attr("style", "animation: progress " + this.duration + "ms linear forwards")
    };

    onSpacePressed(){
        console.log("Space pressed", this)
        if (this.canStop) {
            this.onStop();
        }
        else if (this.stopped) {
            this.onContinue();
        }
    }

    onStop() {
        if (!this.canStop) return;

        console.log("onStop");
        // Remove timeout
        clearTimeout(this.timeout);

        // Complete animation/show full circle
        var svg = d3.select(".progress");
        svg.selectAll("circle").remove();
        svg.append("circle")
            .attr("r", "17.5")
            .attr("cx", 20).attr("cy", 20)
            .attr("class", "progress_value progress_complete")

        // Show next symbol
        $(".pauseIcon img").replaceWith("<img src='/static/images/fwdicon.png'/>");

        //Set status to stopped
        this.canStop = false;
        this.stopped = true;
    }

    onContinue() {
        if (!this.stopped && !this.canStop) return;
        this.onStop();

        console.log("onContinue");

        this.canStop = false;
        this.stopped = false;

        // Remove symbol
        var svg = d3.select(".progress");
        svg.selectAll("circle").remove();

        // Hide icon
        $(".pauseIcon img").replaceWith("<img src=''/>");

        // Call next function
        this.nextFunc();

    }
}