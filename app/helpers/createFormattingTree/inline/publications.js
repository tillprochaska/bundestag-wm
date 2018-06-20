/**
 * PUBLICATION
 * Replace references to Bundestag publications with
 * links to PDF files on the Bundestag website, e.g.
 * Drucksache 19/12345 or Drucksachen 18/12, 19/12345
 */

const BASE_URL = 'http://dipbt.bundestag.de/doc/btd';

export default (raw, replace) => {
	let pattern = /\n?Drucksachen? (\d{2}\/(?:\d{1,5}|…)(?:, \d{2}\/(?:\d{1,5}|…))*)/gsm;
	return replace(raw, pattern, (match, items) => {
		return {
			type: 'publications',
			publications: items.split(', ').map(publication => {
				let legislature = publication.split('/')[0];
				let number      = publication.split('/')[1];
				let type        = number === '…' ? 'missing' : 'available';
				let filename    = `${ legislature }${ number.padStart(5, '0') }.pdf`;
				let url = `${ BASE_URL }/${ legislature }/${ number.padStart(5, '0').substr(0, 3) }/${ filename }`;

				if(type === 'missing') {
					return { type, legislature, number };
				} else {
					return { type, legislature, number, filename, url };
				}
			})
		};
	});
}