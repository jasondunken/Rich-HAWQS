inputData = {
    'dataset': 'HUC8',
    'downstreamSubbasin': '07100009',
    'setHrus': {
        'method': 'area',
        'target': 2,
        'units': 'km2'
    },
    'weatherDataset': 'PRISM',
    'startingSimulationDate': '1981-01-01',
    'endingSimulationDate': '1985-12-31',
    'warmupYears': 2,
    'outputPrintSetting': 'daily',
    'reportData': {
        'formats': [ 'csv', 'netcdf' ],
        'units': 'metric',
        'outputs': {
            'rch': {
                'statistics': [ 'daily_avg' ]
            }
        }
    }
}