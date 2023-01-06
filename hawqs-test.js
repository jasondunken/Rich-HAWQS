// HAWQS API project submit test script
// Original code example from https://dev-api.hawqs.tamu.edu/#/docs/projects/submit
// Refactored from node => plain html/js, axios => fetch

let submissionResult = null;

async function go() {
    // HTML elements with declared ids have a corresponding global var initialized
    // you technically don't need to use document.getElementById as long as ids are unique
    // for this script to run you only need to call it from an html page with <div id='pageContent'>
    pageContent.innerHTML = "<h1>Starting HAWQS API test...</h1>";
    pageContent.innerHTML += "<h2>Checking API...<h2>\n";
    pageContent.innerHTML += "<p>" + JSON.stringify(await pingAPI()) + "</p>";
    pageContent.innerHTML += "<h2>Submitting Project...</h2>\n";
    pageContent.innerHTML += "<p>" + JSON.stringify(await testSubmit()) + "</p>";
}

async function pingAPI() {
    const getOptions = { headers: { "X-API-Key": DEFAULT_API_KEY } };
    const response = await fetch(`https://${DEFAULT_API_URL}/test/clientget`, getOptions);
    return await response.json();
}

async function testSubmit() {
    //The following input data is a snippet for demonstration purposes.
    //Use the Input Builder tab, Input JSON tab, and/or Input Definitions API for help constructing your input object.
    const inputData = {
        dataset: "HUC8",
        downstreamSubbasin: "07100009",
        setHrus: {
            method: "area",
            target: 2,
            units: "km2",
        },
        weatherDataset: "NCDC NWS/NOAA",
        startingSimulationDate: "1961-01-01",
        endingSimulationDate: "1965-12-31",
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
        body: inputData,
        headers: { "X-API-Key": DEFAULT_API_KEY, "Content-type": "application/json" },
    };
    const postResponse = await fetch(`https://${DEFAULT_API_URL}/projects/submit`, postOptions);
    if (postResponse.ok) {
        submissionResult = await postResponse.json();
    } else {
        return await postResponse.json();
    }

    //Your project status URL is now stored in your submissionResult.
    //It is up to you how to check the progress. The following example shows checking on an interval every 60 seconds.
    //As an alternative to the polling the data example below, we do make use of Microsoft SignalR on the server to push updates to clients.
    //This is more advanced than this example, so please contact the development team if needed.

    // if (submissionResult !== null) {
    //     let isComplete = false;
    //     let projectStatus = null;
    //     let intervalTimer = setInterval(async () => {
    //         projectStatus = await checkStatus();
    //     }, 60000);

    //     if (projectStatus != null) {
    //         if (projectStatus.status.errorStackTrace !== null) {
    //             //There was an error running your project.
    //             console.error(projectStatus.status.errorStackTrace);
    //             clearInterval(intervalTimer);
    //         } else if (projectStatus.status.progress >= 100) {
    //             for (let file of projectStatus.output) {
    //                 //Choose what to do with files here
    //                 let name = file.name;
    //                 let url = file.url;
    //             }
    //             clearInterval(intervalTimer);
    //         }
    //     }
    // }
}

async function checkStatus() {
    const getResponse = await fetch(submissionResult.url);
    if (getResponse.data) return getResponse.data;
    pageContent.innerHTML = "failed to fetch!";
}

go();
