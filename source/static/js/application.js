$(function() {

	var dashboard = new PowerDashboard({
		apiConfig: {
			host: 'file:///home/vg/Downloads/puewue-frontend_2/puewue-frontend/demo/api',
			// uriPrefix: 'api'
		},
		metrics: [
			{
				alias: 'humidity',
				name: 'Humidity',
				minDomainDifference: 0.05
			},
			{
				alias: 'temperature',
				name: 'Temperature',
				minDomainDifference: 0.05
			},
			{
				alias: 'pue',
				name: 'PUE',
				domain: {
					min: 1.0,
					max: 1.2
				}
			},
			{
				alias: 'wue',
				name: 'WUE',
				domain: {
					min: 0,
					max: 1.5
				}
			}
		]
	});

});