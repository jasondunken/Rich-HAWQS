// HAWQS API project submit test script
// Original code example from https://dev-api.hawqs.tamu.edu/#/docs/projects/submit
// Refactored from node => plain html/js, axios => fetch

// for this script to run you only need to call it from an html page with <div id='pageContent'>

// const DEFAULT_API_URL = "current.hawqs.api.url"
// const DEFAULT_API_KEY = "=Your+API_key="

let submissionResult = null;
const STATUS_CHECK_INTERVAL = 60000; // ms/check
let statusCheckInterval = null;

async function go() {
    writeToPage("<h1>Starting HAWQS API test...</h1>");
    writeToPage("<h2>Checking API...<h2>");
    writeToPage("<p>" + JSON.stringify(await pingAPI()) + "</p>");
    writeToPage("<h2>Submitting Project...</h2>");
    writeToPage("<p>" + JSON.stringify(await testSubmit()) + "</p>");
    monitorStatus();
}

async function pingAPI() {
    const getOptions = { headers: { "X-API-Key": DEFAULT_API_KEY } };
    const response = await fetch(`https://${DEFAULT_API_URL}/test/clientget`, getOptions);
    return await response.json();
}

async function testSubmit() {
    const inputData = {
        dataset: "HUC8",
        downstreamSubbasin: "07100009",
        setHrus: {
            method: "area",
            target: 2,
            units: "km2",
        },
        weatherDataset: "PRISM",
        startingSimulationDate: "1981-01-01",
        endingSimulationDate: "1985-12-31",
        warmupYears: 2,
        outputPrintSetting: "daily",
        reportData: {
            formats: ["csv", "netcdf"],
            units: "metric",
            outputs: {
                rch: {
                    statistics: ["daily_avg"],
                },
            },
        },
    };

    const postOptions = {
        method: "POST",
        body: JSON.stringify(inputData),
        headers: { "X-API-Key": DEFAULT_API_KEY, "Content-type": "application/json" },
    };
    const postResponse = await fetch(`https://${DEFAULT_API_URL}/projects/submit`, postOptions);
    submissionResult = await postResponse.json();
    return submissionResult;
}

async function monitorStatus() {
    writeToPage("<h3>Monitoring Project Status</h3>");
    if (submissionResult.url) {
        writeToPage(`<p>Project status URL: ${submissionResult.url}</p>`);
        statusCheckInterval = setInterval(checkStatus, STATUS_CHECK_INTERVAL);
    } else {
        writeToPage("<p>There was no URL returned from project submission!</p>");
    }
}

async function checkStatus() {
    const getOptions = { headers: { "X-API-Key": DEFAULT_API_KEY } };
    const response = await fetch(submissionResult.url, getOptions);
    if (response.ok) {
        const projectStatus = await response.json();
        const progress = projectStatus.status.progress;
        writeToPage(`<p>Current progress ${progress}%</p>`);
        if (progress >= 100) {
            clearInterval(statusCheckInterval);
            projectCompleted(projectStatus.output);
        }
    } else {
        clearInterval(statusCheckInterval);
    }
}

function projectCompleted(output) {
    writeToPage("</h2>Project Completed</h2>");
    let outputHtml = "<p>";
    for (let file of output) {
        outputHtml += `<div>Output: ${file.name} | URL: ${file.url}</div>`;
    }
    writeToPage(outputHtml + "</p>");
}

function writeToPage(content) {
    // HTML elements with declared ids have a corresponding global var initialized
    // you don't need to use document.getElementById if the id is unique
    pageContent.innerHTML += content;
}

go();
