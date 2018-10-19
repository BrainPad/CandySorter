$(function () {
    $("body").removeClass("mode-speech-start");

    // API settings
    var pid = Math.floor(Math.random() * 10000000000000000); // POST ID
    
    var config = new FycConfig();


    function onLoad() {
        checkCam();
        checkRobot();
        checkConnection();

        initSpeechSelect();
        initUILangSelect();
        initEndText();
        initResetButton();
        initTiming();
    };

    function initSpeechSelect() {
        $('#speech-lang').val(config.getSpeechLang().translate);

        $('#speech-lang').on('change', function() {
            new_value = $('#speech-lang').val();
            if (new_value === "no") {
                config.setSpeechLang({
                    stream: 'nb-NO',
                    translate: 'no',
                });
            }
            else if (new_value === "en") {
                config.setSpeechLang({
                    stream: 'en-US',
                    translate: 'en',
                });
            }
        });
    };

    function initUILangSelect() {
        $('#ui-lang').val(config.getUIlang());

        $('#ui-lang').on('change', function () {
            new_value = $('#ui-lang').val();
            console.log("New value: ", new_value)
            if (new_value === "no") {
                console.log("Setting language to no");
                config.setUIlang("no");
            }
            else if (new_value === "en") {
                config.setUIlang("en");
            }
        });
    };

    function initEndText() {
        $('#thanks-text').val(config.getEndText());
        $('#end-text-button').on('click', setEndText);
    };

    function initTiming() {
        var values = ["tranSec", "nlSec", "forceSec", "camSec", "selectSec"];
        $(".timeout-setting input").each(function(i) {
            $(this).val(config.getTransitionTimeouts()[values[i]]);
            $(this).on('keyup', null, values[i], function(event) {
                let key = event.data;
                let value = parseInt($(event.target).val());
                if(value>=1000) {
                    config.setTransitionTimeouts(key, value);
                }
            })
        })
    };

    function setEndText() {
        config.setEndText($('#thanks-text').val());
    };

    function setTiming() {

    }

    function initResetButton(){
        $('#reset-btn').on('click', function() {
            reset();
        });
    }

    function checkConnection() {
        updateConnectionStatus(navigator.onLine);
    };

    function checkRobot() {
        $.ajax({
            type: "GET",
            contentType: "application/json",
            dataType: "json",
            url: config.getApiEndpoints().robStatusUrl,
            error: function (textStatus) {
                updateRobotStatus(false);
            },
            success: function (data) {
                updateRobotStatus(true);
            }
        });
    };

    function checkCam() {
        $.ajax({
            type: "GET",
            contentType: "application/json",
            dataType: "json",
            url: config.getApiEndpoints().camStatusUrl,
            error: function (textStatus) {
                updateCameraStatus(false);
            },
            success: function (data) {
                updateCameraStatus(true);
            }
        });
    };

    function updateConnectionStatus(statusOk){
        color = statusOk ? "#49bca1" : "#ff5f63";
        text = statusOk ? "OK" : "Error";

        $(".flex-container div:nth-child(1)").css({
            "background-color": color
        });
        $(".flex-container #OKconn").text(text);
    };

    function updateRobotStatus(statusOk){
        color = statusOk ? "#49bca1" : "#ff5f63";
        text = statusOk ? "OK" : "Error";

        $(".flex-container div:nth-child(2)").css({
            "background-color": color
        });
        $(".flex-container #OKrob").text(text);
    };

    function updateCameraStatus(statusOk){
        color = statusOk ? "#49bca1" : "#ff5f63";
        text = statusOk ? "OK" : "Error";

        $(".flex-container div:nth-child(3)").css({
            "background-color": color
        });
        $(".flex-container #OKcam").text(text);
    };

    function reset() {
        config.reset();  
        initSpeechSelect();
        initEndText();
        initTiming();
        initUILangSelect();
    }

    onLoad()
});
