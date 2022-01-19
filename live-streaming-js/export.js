const puppeteer = require('puppeteer');
console.log(__dirname)
var options = {
    headless: false,
    args: [
        '--enable-usermedia-screen-capturing',
        '--allow-http-screen-capture',
        '--no-sandbox',
        '--auto-select-desktop-capture-source=pickme',
        '--disable-setuid-sandbox',
        '--load-extension=' + __dirname,
        '--disable-extensions-except=' + __dirname,
    ],
    executablePath: 'google-chrome-unstable',
}
puppeteer.launch(options).then(browser => {
    return browser.pages().then(pages => {
        var page = pages[0];
        return page.goto('http://tobiasahlin.com/spinkit/', { waitUntil: 'networkidle2' }).then(_ => {
            return page.evaluate(() => {
                var session = {
                    audio: false,
                    video: {
                        mandatory: {
                            chromeMediaSource: 'screen',
                        },
                        optional: []
                    },
                };
            })
        })
    }).then(_ => {
        // return browser.close()
    })
})