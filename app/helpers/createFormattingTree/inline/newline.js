/**
 * NEWLINE
 * Replace linebreaks
 */

export default (raw, replace) => {
	let pattern = /\n+/g;
	return replace(raw, pattern, (match, items) => {
		return {
			type: 'linebreak'
		};
	});
}