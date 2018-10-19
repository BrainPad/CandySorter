class FycConfig {
    // Key names
    constructor() {
        // Local storage keys
        this.speechLangKey = "speech_lang";
        this.uiLangKey = "ui_lang";
        this.nlLangKey = "nl_lang";
        this.endTextKey = "end_text";
        this.timeoutsKey = "timeouts";
        this.apiUrlsKey = "api_urls";

        // Defaults
        this.speechLangDefault = {
            stream: 'nb-NO',
            translate: 'no',
        }
        this.uiLangDefault= 'no';
        this.language;
        this.nlLangDefault = 'en';
        this.endTextDefault = "Takk for at du kom innom!<br>Hold gjerne kontakten på computas.no";
        this.timeoutDefaults = {
            tranSec: 5000,
            nlSec: 5000,
            forceSec: 5000,
            camSec: 7000,
            selectSec: 8000,
        }

        this.apiUrlDefaults = {
            morUrl: "/api/morphs",
            simUrl: "/api/similarities",
            pickUrl: "/api/pickup",
            tranUrl: "/api/translate",
            camStatusUrl: "/api/status/camera",
            robStatusUrl: "/api/status/robot",
        }

        this.setLanguage();

    }

    setLanguage() {
        $.ajax({
            url:  '/static/lang/' +  this.getUIlang() + '.json',
            dataType: 'json', async: false, dataType: 'json',
            success: function (lang) {
                console.log(lang);
                this.language = lang;

                $(".localize").each(function(i) {
                    let localized_text = lang[$(this).data('lang')];
                    console.log("Changing text on ", this, " to ", localized_text);
                    $(this).text(localized_text)
                })
            },
            error: function(error) {
                console.log(error);
                }
            }
        );
    }

    // Speech Language
    getSpeechLang() {
        return this.getJsonOrDefault(this.speechLangKey, this.speechLangDefault);
    }

    setSpeechLang(lang) {
        localStorage.setItem(this.speechLangKey, JSON.stringify(lang));
    }

    // UI Language
    getUIlang() {
        return this.getOrDefault(this.uiLangKey, this.uiLangDefault);
    }

    setUIlang(lang) {
        localStorage.setItem(this.uiLangKey, lang);
        this.setLanguage();
    }


    // NL Language (used by Natural Language API and Word2Vec)
    getNlLang() {
        return this.getOrDefault(this.nlLangKey, this.nlLangDefault);
    }
    
    // Endtext
    getEndText() {
        return this.getOrDefault(this.endTextKey, this.endTextDefault);
    }

    setEndText(text) {
        localStorage.setItem(this.endTextKey, text);
    }

    // Timeouts
    getTransitionTimeouts(){
        return this.getJsonOrDefault(this.timeoutsKey, this.timeoutDefaults);
    }

    setTransitionTimeouts(transKey, value) {
        let currentValue = this.getTransitionTimeouts();
        let newValue = {
            ...currentValue,
            [transKey]: value,
            
        }
        localStorage.setItem(this.timeoutsKey, JSON.stringify(newValue));
    }
    

    // API
    getApiEndpoints() {
        return this.getJsonOrDefault(this.apiUrlsKey, this.apiUrlDefaults);
    }


    // Reset
    reset() {
        localStorage.clear();
    }

    // Helpers
    getOrDefault(key, fallback) {
        var value = localStorage.getItem(key);
        if (value == null) {
            return fallback;
        } else {
            return value;
        }
    }

    getJsonOrDefault(key, fallback) {
        var value = localStorage.getItem(key);
        if (value == null) {
            return fallback;
        } else {
            return JSON.parse(value);
        }
    }
}