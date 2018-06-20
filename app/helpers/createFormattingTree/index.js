import list from './block/list.js';
import newline from './inline/newline.js';
import publications from './inline/publications.js';

let replace = (raw, pattern, callback, next) => {
	let tree = [];
	let match;

	if(!next) next = (raw => [ raw ]);

	while((match = pattern.exec(raw)) !== null) {
		let before = raw.substr(0, match.index).trim();
		raw = raw.substr(match.index + match[0].length).trim();

		if(before !== '') {
			tree.push(...next(before, replace));
		}

		tree.push(callback(...match.slice(0, match.length)));
		pattern.lastIndex = 0;
	}

	if(raw !== '') {
		tree.push(...next(raw, replace));
	};

	return tree;
};

export default raw => {
	if(raw !== '') {
		return list(raw, (raw, pattern, callback) => {
			return replace(raw, pattern, callback, raw => {
				return publications(raw, (raw, pattern, callback) => {
					return replace(raw, pattern, callback, raw => {
						return newline(raw, replace);
					});
				});
			});
		})
	} else {
		return [];
	}
};