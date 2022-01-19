const puppeteer = require("puppeteer")
// const { record } = require('puppeteer-recorder');

async function main() {
    const browser = await puppeteer.launch({
        headless: false,
        args: [
            '--use-fake-ui-for-media-stream',
            '--use-fake-device-for-media-stream',
            '--use-file-for-fake-audio-capture=/path/example.wav',
            '--allow-file-access',
        ],
        ignoreDefaultArgs: ['--mute-audio'],
    });
    const page = await browser.newPage();
    page.setViewport({ height: 1080, width: 1920 })
    await page.goto('https://www.youtube.com/watch?v=oj9VqXtg1cg', { waitUntil: 'load' });

    // await page.evaluate(() => {
    //     // navigator.mediaDevices.getUserMedia = async function () {
    //     //     return stream;
    //     // };
    // })

    return await page.evaluate(() => {
        var session = {
            audio: true,
            video: {
                mandatory: {
                    chromeMediaSource: 'screen',
                },
                optional: []
            },
        };
    })

    // await record({
    //     browser: browser, // Optional: a puppeteer Browser instance,
    //     page, // Optional: a puppeteer Page instance,
    //     output: 'output.webm',
    //     fps: 60,
    //     frames: 60 * 5, // 5 seconds at 60 fps,
    //     prepare: function () { }, // <-- add this line
    //     render: function () { } // <-- add this line
    // });
}

main()