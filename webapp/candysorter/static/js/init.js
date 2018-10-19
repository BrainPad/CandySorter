$(function () {
    // UI variables
    var winH = window.innerHeight;
    var winW = window.innerWidth;

    // Get config object
    var config = new FycConfig();

    let timeoutManager = new TimeoutManager();

    // API settings
    var pid = Math.floor(Math.random() * 10000000000000000); // POST ID
    var morUrl = "/api/morphs"; // API for Morphological analysis
    var simUrl = "/api/similarities"; // API for Similarity analysis
    var pickUrl = "/api/pickup"; // API for pick up candy
    var tranUrl = "/api/translate"; // API for translation

    // variables
    var inputSpeech = "Kan jeg få sjokolade"; // Spoken sentence
    var speechTxt = ""; // Translated text/text used for nl and similiarities
    var sim = "";


    // Box candy suggestions
    //var examples = ["\"Kan jeg få sjokolade?\"","\"Jeg liker smurf\"","\"Kan jeg få lakris?\"", "\"Kan jeg få noe søtt?\""]
    //Twist suggestions
    //var examples = ["\"Kan jeg noe med nøtter?\"","\"Jeg liker karamell\"","\"Kan jeg få noe salt?\"", "\"Kan jeg få noe søtt?\"", "\"Jeg liker kokos\""]
    // general suggestions
    var examplesNO = ["Beskriv hva du har lyst på","Hvilken smak liker du best?"];
    var examplesEN = ["Describe the candy you want","What flavour do you like the best?"];

    function init() {
        if (config.getUIlang() === "no") examples = examplesNO;
        if (config.getUIlang() === "en") examples = examplesEN;

        /* EXAMPLES OF WHAT TO SAY */
        // variable to keep track of last text displayed
        setTimeout(function () {
            var i = 0;
            var textTimer = function() {
                if (i >= examples.length) { i = 0; }
                $("#example-text").fadeOut(function() {
                    $(this).text(examples[i++]).fadeIn();
                });
            }
            $(".speech-hand-animation").show();
            $("#example-text").text(examples[i++]); // initialize with first quote
            setInterval(textTimer, 3500); // how long each text example is shown
        }, 3000); //wait time until demo starts

        // Set end text
        $('#textend').html(config.getEndText());

    }

    var speech = function() {
        $("body").addClass("mode-speech-start");

        recognition_result = "";

        function speechCallback(data) {
            if (data.event === "end_of_speech") {
                console.log("DONE!")
                inputSpeech = recognition_result

                if(config.getSpeechLang().translate === 'en') {
                    speechTxt = inputSpeech;
                    setTimeout(function () {
                        nl();
                    },500);
                } else {
                    setTimeout(function () {
                        translation();
                    },500);
                }

            }
            else {
                recognition_result = data.transcript
                document.getElementById('speech-interim-text').innerHTML = data.transcript
            }
        }

        var gcpSpeech = new GcpSpeechStreamer(speechCallback, config.getSpeechLang().stream, true, "twist");

        $(".speech-mic").click(function () {
            $(".pauseIcon img").replaceWith("<img src='/static/images/pauseicon.png'/>")
            $(".speech-mic").css({ // Changes the color of the mic-icon when clicked
                    background: "#ff5f63",
                    border: "solid 0 #ff5f63"
                }
            );
            $(".speech-footer").hide();
            $(".speech-hand-animation").hide();
            $("body").addClass("mode-speech-in");

            if (!gcpSpeech.isRecording()) {
                gcpSpeech.start_recognition();
            } else {
                gcpSpeech.stop_recognition();
            }
        });
    }


    /*
    */
    /*
    var speech = function () {
        $("body").addClass("mode-speech-start");
        recognition.lang = lang;
        $(".speech-mic").click(function () {
            $(".speech-mic").css({ // Changes the color of the mic-icon when clicked
                    background: "#D12F33",
                    border: "solid 0 #D12F33"
                }
            );
            $(".speech-footer").hide();
            $(".speech-hand-animation").hide(); //Hide demo animation when record starts
            $("body").addClass("mode-speech-in");
            setTimeout(function () {
                translation();
            },3500);
        });
    }*/

    var translation = function () {
        $.ajax({
            type: "POST",
            contentType: "application/json",
            dataType: "json",
            url: tranUrl,
            data: JSON.stringify({
                "id": pid,
                "text": inputSpeech,
                "source": config.getSpeechLang().translate,
            }),
            error: function (textStatus) {
                console.log(textStatus);
            },
            success: function (data) {
                speechTxt = he.decode(data[0].translatedText);
                $("body").addClass("mode-tran-loaded");
                $(".tran-word").text(inputSpeech);

                /*FOOTER LOADING ANIMATION*/
                setTimeout(function () {
                    $(".tran-footer").show();
                }, 500);


                timeoutManager.startTimer(nl, config.getTransitionTimeouts().tranSec)
                /*
                setTimeout(function () {
                    nl()
                }, 5000);*/
            }
        });
        // inputTxt --> translateAPI
        // success --> speechTxt = data.string
    }


    // NL processing
    var nl = function () {
        var morXHR = null;
        var simXHR = null;

        morXHR = $.ajax({
            type: "POST",
            contentType: "application/json",
            dataType: "json",
            url: morUrl,
            data: JSON.stringify({
                "id": pid,
                "text": speechTxt,
                "lang": config.getNlLang()
            }),
            error: function (jqXHR, textStatus) {
                if (textStatus == 'abort') { return; }
                console.log(jqXHR);
                if (simXHR !== null && simXHR.readyState > 0 && simXHR.readyState < 4) {
                    simAjax.abort();
                }
                sorry();
            },
            success: function (data) {
                // remove translation UI
                $("body").addClass("mode-tran-finish");
                // generate morpheme
                data = data.morphs
                console.log(data);
                for (var i in data) {
                    var morph = "";
                    for (key in data[i].pos) {
                        var txt = data[i].pos[key];
                        if (key != "tag" && txt.indexOf("UNKNOWN") == -1) {
                            morph += key + "=" + txt + "<br>";
                        }
                    }
                    var desc = "<dl>";
                    desc += "<dd class='nl-label'>" + data[i].depend.label + "</dd>";
                    if (data[i].pos.tag === "NOUN") {
                        desc += "<dd class='nl-word' style='font-size: 80px; font-weight: bold'>" + data[i].word + "</dd>"
                    }
                    else {
                        desc += "<dd class='nl-word'>" + data[i].word + "</dd>";
                    }
                    desc += "<dd class='nl-tag'>" + data[i].pos.tag + "</dd>";
                    desc += "<dd class='nl-pos'>" + morph + "</dd>";
                    desc += "</dl>"
                    $(".nl-syntax").append(desc);
                    // generate arrow
                    for (var j in data[i].depend.index) {
                        $(".nl-depend").append("<dd data-from=" + i + " data-to=" + data[i].depend.index[j] + "></dd>");
                    }
                }
                // measure X coordinate
                var dependX = [];
                $(".nl-syntax dl").each(function (index) {
                    var x = $(".nl-syntax dl:nth-child(" + (index + 1) + ")").position().left;
                    var w = $(".nl-syntax dl:nth-child(" + (index + 1) + ")").outerWidth();
                    dependX.push(Math.round(x + w / 2));
                });

                // rearrange arrow
                $(".nl-depend dd").each(function (index) {
                    var from = $(this).data().from;
                    var to = $(this).data().to;
                    if (from < to) {
                        var x = dependX[from];
                        var w = dependX[to] - dependX[from];
                    } else {
                        var x = dependX[to];
                        var w = dependX[from] - dependX[to];
                        $(this).addClass("left");
                    }
                    $(this).css({
                        top: (Math.abs(from - to) - 1) * -30 + "px",
                        left: x + "px",
                        width: w + "px"
                    });
                });
                /*FOOTER LOADING ANIMATION*/
                setTimeout(function () {
                    $(".nl-footer").show();
                }, 500);

                // effect settings
                $(".nl-word").each(function (index) {
                    $(this).css("transition-delay", index / 5 + "s");
                });
                $(".nl-tag, .nl-pos").each(function (index) {
                    $(this).css("transition-delay", 1 + index / 10 + "s");
                });
                $(".nl-label, .nl-depend dd").css("transition-delay", 3 + "s"); //endret fra 2.5
                $("body").addClass("mode-nl-loaded");

                /*MAKES IT LOOK VERY CRASHED WHEN DISABLED WITHOUT FOOTER LOADING ANIMATION*/
                // repeat effects
                /*setInterval(function () {
                    $("body").addClass("mode-nl-repeat");
                    setTimeout(function () {
                        $("body").removeClass("mode-nl-loaded");
                    }, 400);
                    setTimeout(function () {
                        $("body").addClass("mode-nl-loaded");
                        $("body").removeClass("mode-nl-repeat");
                    }, 500);
                }, 6000);*/
            }
        });
        // retrieve inference data
        simXHR = $.ajax({
            type: "POST",
            contentType: "application/json",
            dataType: "json",
            url: simUrl,
            data: JSON.stringify({
                "id": pid,
                "text": speechTxt,
                "lang": config.getNlLang()
            }),
            error: function (jqXHR, textStatus) {
                if (textStatus == 'abort') { return; }
                console.log(jqXHR);
                if (morXHR !== null && morXHR.readyState > 0 && morXHR.readyState < 4) {
                    morXHR.abort();
                }
                sorry();
            },
            success: function (data) {
                sim = data;
                console.log("(sim = data) from simURL. Sim = ");
                console.log(sim);

                timeoutManager.startTimer(force, config.getTransitionTimeouts().nlSec);
            }
        });
    };

    // drow force layout
    var force = function () {
        $("body").addClass("mode-force-start");
        $(".force-footer").show();
        // generate dataset
        var data = sim.similarities.force;
        var dataSet = {
            "nodes": [],
            "links": []
        };
        for (var i in data) {
            dataSet.nodes.push(data[i]);
            dataSet.links.push({
                "source": 0,
                "target": parseInt(i) + 1
            });
        }

        // Add a node for input string at the beginning of the data set
        dataSet.nodes.unshift({
            "label": "",
            "lid": 0,
            "em": 0,
            "x": winW / 2,
            "y": winH / 2,
            "fixed": true
        });
        // create SVG
        var svg = d3.select(".force").append("svg").attr({
            width: winW,
            height: winH
        });
        // layout setttings
        var d3force = d3.layout.force()
            .nodes(dataSet.nodes)
            .links(dataSet.links)
            .size([winW, winH])
            .linkDistance(winH / 2.5)
            .charge(-1000)
            .start();
        var link = svg.selectAll("line")
            .data(dataSet.links)
            .enter()
            .append("line");
        var g = svg.selectAll("g")
            .data(dataSet.nodes)
            .enter() //separating all nodes in the array
            .append("g") //appending g-tag to all nodes
            .attr("class", function (d) { //adding class .label-X to all nodes, varying color
                return "label-" + d.lid;
            });
        var sort = svg.selectAll('g')
            .sort(function(a, b) {
                return a.em > b.em;
            })
        var circle = g.append("circle") //all elements "g" appended circle class
            .attr("r", function (d) { //setting each radius based on similarity
                var r = 70 + d.em * 75;
                return r;
            });
        var label = g.append("text")
            .text(function (d) {
                //if (d.em > 0.50 && d.em < 1)
                return d.label; //appending a text label to each element g
                //else return d.label + " < 0.1";
            });
        // setting coordinate (input string（lid=0）fix the mid of display）
        d3force.on("tick", function () {
            g.attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
            link.attr("x1", function (d) {
                return d.source.x;
            })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });
        });
        // Place the input character string in the center of the screen
        $(".force").prepend("<div class='force-txt'>" + speechTxt + "<div>");
        var txtW = $(".force-txt").outerWidth();
        var txtH = $(".force-txt").outerHeight();
        $(".force-txt").css({
            top: (winH - txtH) / 2 + "px",
            left: (winW - txtW) / 2 + "px"
        });

        $(".plot dd:last-child").addClass("nearest");
        // draw with time difference
        setTimeout(function () {
            $("body").addClass("mode-plot-start");
        }, 6000); // WAS 3000; //How long just the circles are displayed

        timeoutManager.startTimer(cam, config.getTransitionTimeouts().forceSec);
    };

    // output camera image
    var cam = function () {
        $("body").addClass("mode-plot-end");
        $("body").addClass("mode-cam-start");
        var imgUrl = sim.similarities.url;
        // retrieve image size
        var img = new Image();
        img.src = imgUrl;
        img.onload = function () {
            var w = img.width;
            var h = img.height;
            $(".cam-img svg").attr("viewBox", "0 0 " + w + " " + h);
            if (w > winW) {
                h = h / w * winW;
                w = winW;
            }
            if (h > winH) {
                w = w / h * winH;
                h = winH;
            }
            $(".cam-img").width(w).height(h);
        };


        /* SVG TEST SPACE*/
        // Generate datasets
        var camdata = sim.similarities.embedded;
        var dataSet2 = []; // keeping track of all candies highest em and lid.
        for (var i in camdata) {
            var em = 0;
            var label = "";
            var lid = "";
            for (var j in camdata[i].similarities) {
                if (camdata[i].similarities[j].em > em) {
                    label = camdata[i].similarities[j].label;
                    lid = camdata[i].similarities[j].lid;
                    em = camdata[i].similarities[j].em;
                }
            }
            dataSet2.push({
                "lid": lid,
                "em": em,
                "label": label
            });
        }

        // setting image
        $(".cam-img").css("background-image", "url(" + imgUrl + ")");


        /*
        * Having different attr on polygon and circles
        * .attr("class", "label-" + camdata[i].similarities[i].lid)
        * .attr("class", "label-" + dataSet2[i].lid)
        * determines if the colors should all be different, or if the candy with
        * the same label should be the same
        *
        */

        // adding svg elements
        var svg = d3.select(".cam-img svg");
        for (var i in camdata) {
            svg.append("polygon")
                .attr("points", camdata[i].box[0][0] + "," + camdata[i].box[0][1] + " " + camdata[i].box[1][0] + "," + camdata[i].box[1][1] + " " + camdata[i].box[2][0] + "," + camdata[i].box[2][1] + " " + camdata[i].box[3][0] + "," + camdata[i].box[3][1] + " ")
                .attr("class", "label-" + dataSet2[i].lid);
        }
        for (var i in camdata) {
            svg.append("circle")
                .attr("r", "80")
                .attr("cx", camdata[i].box[0][0]).attr("cy", camdata[i].box[0][1])
                .attr("class", "label-" + dataSet2[i].lid + " delay");
            svg.append("text")
                .attr("x", camdata[i].box[0][0]).attr("y", camdata[i].box[0][1] + 15)
                .text(dataSet2[i].label);
            svg.append("text")
                .attr("x", camdata[i].box[0][0]).attr("y", camdata[i].box[0][1] - 15)
                .text((dataSet2[i].em * 100).toFixed(1) + "%");
        }

        setTimeout(function () {
            $("body").addClass("mode-cam-mid");
        }, 750);

        console.log("Starting cam timer");
        timeoutManager.startTimer(select, config.getTransitionTimeouts().camSec);
    };

    var select = function() {
        $("body").addClass("mode-cam-end");
        $("body").addClass("mode-cam-finished");

        var svg = d3.select(".cam-img svg");
        var nearest = sim.similarities.nearest;

        svg.selectAll("polygon").remove();
        svg.selectAll("text").remove();
        svg.selectAll("circle").remove();
        svg.append("polygon")
            .attr("points",nearest.box[0][0] + "," + nearest.box[0][1] + " " + nearest.box[1][0] + "," + nearest.box[1][1] + " " + nearest.box[2][0] + "," + nearest.box[2][1] + " " + nearest.box[3][0] + "," + nearest.box[3][1] + " ")
            .attr("style", "stroke: #49bca1; stroke-width: 20px;")
        svg.append("circle")
            .attr("r", "120")
            .attr("cx", nearest.box[0][0]).attr("cy", nearest.box[0][1])
            .attr("style", "fill: #49bca1; opacity: 1; ");
        if(config.getUIlang() === "no") {
            svg.append("text")
                .attr("x", nearest.box[0][0]).attr("y", nearest.box[0][1])
                .attr("style", "fill: #003459; font-size: 25px;")
                .text("Jeg velger denne!");
        }
        if(config.getUIlang() === "en") {
            svg.append("text")
                .attr("x", nearest.box[0][0]).attr("y", nearest.box[0][1])
                .attr("style", "fill: #003459; font-size: 25px;")
                .text("I choose this!");
        }

        pickup();

        timeoutManager.startTimer(thanks, config.getTransitionTimeouts().selectSec);
    }

    var pickup = function() {
        console.log("starting pickup")
        // operation of pickup
        $.ajax({
            type: "POST",
            contentType: "application/json",
            dataType: "json",
            url: pickUrl,
            data: JSON.stringify({
                "id": pid
            }),
            error: function (textStatus) {
                console.log(textStatus);
            },
            success: function (data) {
                sim = data;
                console.log(sim);
            }
        });
    }

    // draw endroll
    var thanks = function () {
        $("body").addClass("mode-thanks-start");

        /* Automatic return to startpage
        setTimeout(function () {
            location.reload();
        },15000);
        */
    };

    // draw sorry
    var sorry = function () {
        $("body").addClass("mode-sorry-p");
    };


    init();

    speech();
});
