/**
 * LIST
 * Replaces markdown-like lists with (e. g. multiple lines
 * preceded by a dash) with the corresponding markup
 */

import createFormattingTree from '../index.js';

export default (raw, replace) => {
	let pattern = /(?:^|\n)(–|[a-z]\)) ([\s\S]*)(?:\n\1 [\s\S]*)*/gm;
	return replace(raw, pattern, (match, type, items) => {
		return {
			type: 'list',
			items: items.split(/\n(?:–|[a-z]\)) /).map(createFormattingTree),
		};
	});
}