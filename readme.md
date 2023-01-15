# Rich-HAWQS

### A CLI application to interface with [HAWQS API](https://dev-api.hawqs.tamu.edu/#/)

-   Rich because it uses the [rich](https://github.com/Textualize/rich) python package

A Python CLI application for testing the HMS/HAWQS APIs. With minor changes it could be used to submit and retrieve arbitrary HAWQS projects. For now it uses a static test case.
To use this application you need to provide an env file with the current url for the HAWQS API, your HAWQS API key, and some other stuff that's needed

pip and Anaconda environment files are provided

There's a javascript test in here too, but it completely different from the python one. It's a single automated test that starts as soon as the page loads. It also needs an env similar to the python one, but for simplicity it's just an import.
